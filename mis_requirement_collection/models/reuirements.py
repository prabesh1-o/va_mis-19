from odoo import api, fields, models


class MISRequirements(models.Model):
    _name = "mis.requirements"
    _description = "Mis requirements"
    _rec_name = "title"

    title = fields.Char(string="Title", required=True)
    description = fields.Html(string="Description", required=True)
    department = fields.Many2one("hr.department", string="Department")
    requested_by = fields.Many2one(
        "hr.employee",
        string="Requested By",
        required=True,
        default=lambda self: self.env.user.employee_id,
    )
    state = fields.Selection(
        [
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        string="Status",
        default="to_approve",
        tracking=True,
    )

    @api.onchange("requested_by")
    def _onchange_requested_by(self):
        for req in self:
            if req.requested_by:
                req.department = req.requested_by.department_id

    def action_approve(self):
        for req in self:
            req.state = "approved"

    def action_refuse(self):
        for req in self:
            req.state = "refused"
