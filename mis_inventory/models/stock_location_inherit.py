from odoo import fields, models


class StockLocationInherit(models.Model):
    _inherit = "stock.location"

    user_ids = fields.Many2many("res.users")
