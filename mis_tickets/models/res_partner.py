from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    ticket_ids = fields.One2many(
        "mis.ticket", "customer_id", string="Tickets", tracking=True
    )
