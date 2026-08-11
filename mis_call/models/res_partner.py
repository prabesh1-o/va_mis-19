from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    call_ids = fields.One2many(
        "mis.call", "customer_id", string="Normal Calls", tracking=True
    )
    assign_call_ids = fields.One2many(
        "mis.assign.call", "customer_id", string="Campaign Calls", tracking=True
    )
    mobile = fields.Char(
        string="Mobile"
    )
