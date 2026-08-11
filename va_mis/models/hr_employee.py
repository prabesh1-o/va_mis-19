from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    joined_date = fields.Date(string="Joined Date")

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            employee.work_contact_id.employee = True
        return employees
