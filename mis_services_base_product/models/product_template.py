from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_id = fields.Many2one("mis.services")
    service_menu_id = fields.Many2one(related="service_id.service_menu_id")
