import logging
from datetime import date, datetime
from struct import unpack

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .zkconst import CMD_PREPARE_DATA

_logger = logging.getLogger(__name__)
try:
    from zk import ZK
except ImportError:
    _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    device_id = fields.Char(string="Biometric Device ID")


class ZkMachine(models.Model):
    _name = "zk.machine"
    _description = "ZK Machine"

    name = fields.Char(string="Machine IP", required=True)
    port_no = fields.Integer(string="Port No", required=True)
    address_id = fields.Many2one("res.partner", string="Working Address")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id.id,
    )

    def device_connect(self, zk):
        try:
            conn = zk.connect()
            return conn
        except:
            return False

    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                timeout = 30
                try:
                    zk = ZK(
                        machine_ip,
                        port=zk_port,
                        timeout=timeout,
                        password=0,
                        force_udp=False,
                        ommit_ping=False,
                    )
                except NameError:
                    raise UserError(_("Please install it with 'pip3 install pyzk'."))
                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # conn.clear_attendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                        conn.disconnect()
                        raise UserError(_("Attendance Records Deleted."))
                    else:
                        raise UserError(
                            _(
                                "Unable to clear Attendance log. Are you sure attendance log is not empty."
                            )
                        )
                else:
                    raise UserError(
                        _(
                            "Unable to connect to Attendance Device. Please use Test Connection button to verify."
                        )
                    )
            except:
                raise ValidationError(
                    "Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty."
                )

    def getSizeUser(self, zk):
        """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent"""
        command = unpack("HHHH", zk.data_recv[:8])[0]
        if command == CMD_PREPARE_DATA:
            size = unpack("I", zk.data_recv[8:12])[0]
            print("size", size)
            return size
        else:
            return False

    def zkgetuser(self, zk):
        """Start a connection with the time clock"""
        try:
            users = zk.get_users()
            print(users)
            return users
        except:
            return False

    @api.model
    def cron_download(self):
        machines = self.env["zk.machine"].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env["zk.machine.attendance"]
        att_obj = self.env["hr.attendance"]
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = 15
            try:
                zk = ZK(
                    machine_ip,
                    port=zk_port,
                    timeout=timeout,
                    password=0,
                    force_udp=False,
                    ommit_ping=False,
                )
            except NameError:
                raise UserError(
                    _(
                        "Pyzk module not Found. Please install it with 'pip3 install pyzk'."
                    )
                )
            conn = self.device_connect(zk)
            if conn:
                # conn.disable_device() #Device Cannot be used during this time.
                try:
                    user = conn.get_users()
                except:
                    user = False
                try:
                    attendance = conn.get_attendance()
                except:
                    attendance = False
                if attendance:
                    if self._context.get("is_todays_attendance", False):
                        filtered_attendance = [
                            record
                            for record in attendance
                            if record.timestamp.date() == date.today()
                        ]
                        if filtered_attendance:
                            attendance = filtered_attendance
                        empty_checkouts = att_obj.search([("check_out", "=", False),])
                        for att in empty_checkouts:
                            if att.check_in.date() != date.today():
                                att.check_out = att.check_in

                    for each in attendance:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(
                            atten_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        local_tz = pytz.timezone(self.env.user.partner_id.tz or "GMT")
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time)
                        if user:
                            for uid in user:
                                if uid.user_id == each.user_id:
                                    get_user_id = self.env["hr.employee"].search(
                                        [("device_id", "=", each.user_id)]
                                    )
                                    if get_user_id:
                                        duplicate_atten_ids = zk_attendance.search(
                                            [
                                                ("device_id", "=", each.user_id),
                                                ("punching_time", "=", atten_time),
                                            ]
                                        )
                                        if duplicate_atten_ids:
                                            continue
                                        else:
                                            if self._context.get(
                                                "is_todays_attendance", False
                                            ):
                                                last_check_in_date = (
                                                    get_user_id.last_check_in.date()
                                                    if get_user_id.last_check_in
                                                    else None
                                                )
                                                last_check_out_date = (
                                                    get_user_id.last_check_out.date()
                                                    if get_user_id.last_check_out
                                                    else None
                                                )
                                                if each.punch == 0:
                                                    if (
                                                        last_check_in_date
                                                        == date.today()
                                                    ):
                                                        continue
                                                if each.punch == 1:
                                                    checkin = zk_attendance.search(
                                                        [
                                                            (
                                                                "employee_id",
                                                                "=",
                                                                get_user_id.id,
                                                            ),
                                                            ("punch_type", "=", 0),
                                                            (
                                                                "punching_time",
                                                                ">",
                                                                atten_time,
                                                            ),
                                                        ]
                                                    )
                                                    if (
                                                        checkin
                                                        or last_check_in_date
                                                        != date.today()
                                                    ):
                                                        continue
                                                    if (
                                                        last_check_out_date
                                                        and last_check_out_date
                                                        == date.today()
                                                    ):
                                                        continue

                                            zk_attendance.create(
                                                {
                                                    "employee_id": get_user_id.id,
                                                    "device_id": each.user_id,
                                                    "attendance_type": str(each.status),
                                                    "punch_type": str(each.punch),
                                                    "punching_time": atten_time,
                                                    "address_id": info.address_id.id,
                                                }
                                            )
                                            att_var = att_obj.search(
                                                [
                                                    (
                                                        "employee_id",
                                                        "=",
                                                        get_user_id.id,
                                                    ),
                                                    ("check_out", "=", False),
                                                ]
                                            )
                                            print("ddfcd", str(each.status))
                                            att_source = "biometric"
                                            if each.punch == 0:  # check-in
                                                if not att_var:
                                                    att_obj.create(
                                                        {
                                                            "employee_id": get_user_id.id,
                                                            "check_in": atten_time,
                                                            "attendance_source": att_source,
                                                        }
                                                    )
                                            if each.punch == 1:  # check-out
                                                if len(att_var) == 1:
                                                    existing_source = (
                                                        att_var.attendance_source
                                                    )
                                                    if existing_source == "web":
                                                        att_source = f"{existing_source}/{att_source}"
                                                    att_var.write(
                                                        {
                                                            "check_out": atten_time,
                                                            "attendance_source": att_source,
                                                        }
                                                    )
                                                else:
                                                    att_var1 = att_obj.search(
                                                        [
                                                            (
                                                                "employee_id",
                                                                "=",
                                                                get_user_id.id,
                                                            )
                                                        ]
                                                    )
                                                    if att_var1:
                                                        existing_source = att_var1[
                                                            -1
                                                        ].attendance_source
                                                        if existing_source == "web":
                                                            att_source = f"{existing_source}/{att_source}"
                                                        att_var[-1].write(
                                                            {
                                                                "check_out": atten_time,
                                                                "attendance_source": att_source,
                                                            }
                                                        )

                                    else:
                                        print("ddfcd", str(each.status))
                                        print("user", uid.name)
                                        employee = self.env["hr.employee"].create(
                                            {
                                                "device_id": each.user_id,
                                                "name": uid.name,
                                            }
                                        )
                                        zk_attendance.create(
                                            {
                                                "employee_id": employee.id,
                                                "device_id": each.user_id,
                                                "attendance_type": str(each.status),
                                                "punch_type": str(each.punch),
                                                "punching_time": atten_time,
                                                "address_id": info.address_id.id,
                                            }
                                        )
                                        att_obj.create(
                                            {
                                                "employee_id": employee.id,
                                                "check_in": atten_time,
                                            }
                                        )
                                else:
                                    pass
                    # zk.enableDevice()
                    conn.disconnect
                    return True
                else:
                    raise UserError(
                        _("Unable to get the attendance log, please try again later.")
                    )
            else:
                raise UserError(
                    _(
                        "Unable to connect, please check the parameters and network connections."
                    )
                )
