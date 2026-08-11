from datetime import time

import pytz
from odoo import api, fields, models


class LateAttendace(models.Model):
    _name = "hr.attendance.late"

    late_reason = fields.Text(string="Late Reason")
    attendance_id = fields.Many2one("hr.attendance", required=True, ondelete="cascade")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_source = fields.Selection(
        [
            ("web", "Web"),
            ("biometric", "Biometric"),
            ("biometric/web", "Biometric/Web"),
            ("web/biometric", "Web/Biometric"),
        ],
        string="Source",
        default="web",
        readonly=True,
    )
    late_reason_ids = fields.One2many(
        "hr.attendance.late", "attendance_id", "Late Reason"
    )
    is_late = fields.Boolean(compute="_compute_is_late", store=True, default=False)

    @api.depends("check_in", "employee_id")
    def _compute_is_late(self):
        for record in self:
            if record.check_in and record.employee_id.resource_calendar_id:
                work_hours = record.employee_id.resource_calendar_id.attendance_ids.filtered(
                    lambda emp: emp.day_period == "morning"
                    and emp.dayofweek == str(record.check_in.weekday())
                )
                if work_hours:
                    check_in_time = self._get_checkin_user_timezone(record)
                    work_start_time = time(int(work_hours.hour_from))
                    if check_in_time > work_start_time:
                        record.is_late = True

    def _get_checkin_user_timezone(self, record):
        employee_timezone = record.employee_id.tz or "UTC"
        tz = pytz.timezone(employee_timezone)
        check_in_utc = record.check_in.replace(tzinfo=pytz.UTC)
        check_in_local = check_in_utc.astimezone(tz).time()
        return check_in_local

    def action_add_reason(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Edit Reason",
            "res_model": "hr.attendance.late",
            "view_mode": "form",
            "target": "new",
            "context": {"default_attendance_id": self.id},
        }

    def action_view_reason(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Late Reason",
            "res_model": "hr.attendance.late",
            "view_mode": "form",
            "res_id": self.late_reason_ids[0].id,
            "target": "new",
            "context": {"create": False, "edit": False},
        }
