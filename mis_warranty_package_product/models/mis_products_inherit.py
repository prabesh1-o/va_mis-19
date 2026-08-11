from odoo import fields, models


class MisProduct(models.Model):
    _inherit = "mis.product"

    warranty_package_id = fields.Many2one("mis.warranty.package", string="Warranty")
