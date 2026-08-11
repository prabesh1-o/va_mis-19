from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _attendance_action_change(self, geo_information=None):
        res = super()._attendance_action_change(geo_information)

        if res.attendance_source == "biometric":
            res.attendance_source = "biometric/web"

        return res

    def action_self_attendance_toggle(self):
        self.ensure_one()
        self._attendance_action_change()
        return True
