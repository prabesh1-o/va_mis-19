import ast
from datetime import date, timedelta

from odoo import fields, models


class MisDeviceSim(models.Model):
    _name = "mis.device.sim"
    _description = "MIS Device Sims"
    _rec_name = "sim_no"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sim_no = fields.Char(string="SIM no")
    sim_carrier = fields.Selection([("ncell", "NCELL"), ("ntc", "NTC")])
    data_plan = fields.Char(string="Data Plan")
    device_ids = fields.One2many("mis.device", "sim", string="Devices")
    serial_no = fields.Char(string="Serial Number")
    puk1 = fields.Char(string="PUK 1")
    puk2 = fields.Char(string="PUK 2")
    pin1 = fields.Char(string="PIN 1")
    pin2 = fields.Char(string="PIN 2")
    active = fields.Boolean(default=True)
    sim_recharge_id = fields.Many2one("mis.device.sim.recharge", string="SIM Recharge")
    sim_recharge_history_ids = fields.One2many(
        "mis.device.sim.recharge.history", "sim_id"
    )
    sim_recharge_history_count = fields.Integer(
        "Total Recharge", compute="_compute_sim_recharge_history_count"
    )
    automatic_recharge = fields.Boolean("Automatic", default=False)

    def _compute_sim_recharge_history_count(self):
        """
        Compute the total number of recharge history records for each SIM.
        """
        for sim in self:
            sim.sim_recharge_history_count = len(sim.sim_recharge_history_ids)

    def _get_group_partner_ids(self, xml_ids):
        return self.env["res.partner"].browse(
            list(
                {
                    partner.id
                    for xml_id in xml_ids
                    for partner in self.env.ref(xml_id).users.partner_id
                }
            )
        )

    def _send_sim_reminder(self):
        """
        Sends reminder for SIMs whose recharge is about to expire, the number of days
        before the reminder gets sent is configurable from `res_config_settings`.

        Note: This method is executed automatically as a cron job.
        """
        today = date.today()

        xml_ids = [
            "mis_device.group_mis_sim_manager",
            "mis_device.group_mis_sim_admin",
        ]
        partner_ids = self._get_group_partner_ids(xml_ids)

        days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sim_recharge_expiry_days_count")
        )

        expiring_sims = self.search(
            [
                ("automatic_recharge", "=", False),
                ("sim_recharge_history_ids", "!=", False),
            ]
        ).filtered(
            lambda sim: any(
                today <= history.recharge_expiry <= (today + timedelta(days=days_count))
                for history in sim.sim_recharge_history_ids
                if history.recharge_expiry
            )
        )
        if expiring_sims:
            self._create_reminder_message(expiring_sims, partner_ids)
            self._create_activity(expiring_sims, partner_ids)

    def _create_activity(self, sims, partner_ids):
        """Creates an activity to notify about expiring SIM recharge for the responsible users,
        which is configurable from `res_config_settings`.

        Args:
            sims (recordset): The recordset of SIMs whose recharge is about to expire.
            days_count (int): The number of days for the activity deadline, i.e, before the SIM recharge
            expires.
            partner_ids (recordset): The recordset of partners to whom the message should be sent.

        Note: This method is executed automatically as a cron job.
        """

        user_ids = ast.literal_eval(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("responsible_sim_assignees")
        )

        for user_id in user_ids:
            for sim in sims:
                self.env["mail.activity"].create(
                    {
                        "activity_type_id": self.env.ref(
                            "mail.mail_activity_data_todo"
                        ).id,
                        "res_id": sim.id,
                        "res_model_id": self.env["ir.model"]._get_id(self._name),
                        "note": "SIM recharge is about to expire, please recharge soon!",
                        "user_id": user_id,
                        "summary": "SIM Recharge Reminder",
                        "date_deadline": sim.sim_recharge_history_ids.recharge_expiry,
                    }
                )
                sim.message_subscribe(partner_ids=partner_ids.ids)

    def _create_reminder_message(self, sims, partner_ids):
        """
        Creates a custom reminder message with the details of the SIMs that are about to expire.

        Args:
            sims (recordset): The recordset of SIMs whose recharge is about to expire.
            partner_ids (recordset): The recordset of partners to whom the message should be sent.

        Note: This method is executed automatically as a cron job.
        """

        html = """
        <div class="text-center">
            <h2 class="text-danger">SIM Recharge Reminder</h2>
            <table class="table table-hover table-bordered">
            <tr>
                <th>SIM No</th>
                <th>Recharge</th>
                <th>Carrier</th>
                <th>Recharge Price</th>
                <th>Expires On</th>
            </tr>
        """
        for sim in sims:
            html += f"""
            <tr>
                <td>{sim.sim_no}</td>
                <td>{sim.sim_recharge_id.name or 'N/A'}</td>
                <td>{sim.sim_carrier.capitalize()}</td>
                <td>{sim.sim_recharge_id.recharge_price or 'N/A'}</td>
                <td>{sim.sim_recharge_history_ids.recharge_expiry or 'N/A'}</td>
            </tr>
            """
        html += "</table></div>"
        self._send_message(html, partner_ids)

    def _send_message(self, html, partners):
        """
        Sends a message notification containing a reminder message.

        Args:
            html (`str`): The custom html body containing the reminder message.
            partners (recordset): The recordset of partners to whom the message should be sent.

        Note: This method is executed automatically as a cron job.
        """

        odoobot_id = self.env["ir.model.data"]._xmlid_to_res_id("base.partner_root")
        notification_ids = [
            (0, 0, {"res_partner_id": partner.id, "notification_type": "inbox"})
            for partner in partners
        ]
        self.env["mail.message"].create(
            {
                "message_type": "comment",
                "notification_ids": notification_ids,
                "body": html,
                "partner_ids": [(4, partner_id) for partner_id in partners.ids],
                "subject": "Recharge Expiry List",
                "model": self._name,
                "res_id": self.id,
                "author_id": odoobot_id,
            }
        )

    def action_view_recharge_history(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(self.env.context, default_sim_id=self.id, group_by=False),
                domain=[("sim_id", "=", self.id)],
            )
            return res
        return False
