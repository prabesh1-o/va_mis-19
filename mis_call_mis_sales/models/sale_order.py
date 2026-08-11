from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    call_id = fields.Many2one("mis.call", string="Call id")
