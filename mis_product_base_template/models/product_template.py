from odoo import fields, models


class MISProductTemplate(models.Model):
    _inherit = "product.template"

    mis_product_id = fields.Many2one("mis.product", string="Product", readonly=False)
