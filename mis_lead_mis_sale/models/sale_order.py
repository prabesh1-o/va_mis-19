from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    raw_lead_id = fields.Many2one("lead.raw.data", string="Raw Lead")
