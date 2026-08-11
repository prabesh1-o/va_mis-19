from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    joined_date = fields.Date(string="Joined Date")

    # Only adds a `search` capability to the existing hr_presence_state field.
    # Selection, compute, and default are inherited from the base `hr` module —
    # do not redeclare them here or you risk mismatched selection values.
    hr_presence_state = fields.Selection(search="_search_hr_presence_state")

    def _search_hr_presence_state(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError(
                "Only '=' and '!=' are supported for hr_presence_state search"
            )

        employees = self.with_context(active_test=False).search([])

        if operator == "=":
            matching = employees.filtered(lambda e: e.hr_presence_state == value)
        else:
            matching = employees.filtered(lambda e: e.hr_presence_state != value)

        return [("id", "in", matching.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            employee.work_contact_id.employee = True
        return employees