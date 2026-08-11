from odoo import fields, models


class MisDevice(models.Model):
    _inherit = "mis.device"

    device_model_id = fields.Many2one("mis.product.model", string="Model")
    product_id = fields.Many2one(
        related="device_model_id.product_id", string="Product Name", store=True
    )
    manufacturer = fields.Many2one(
        related="device_model_id.manufacturer_id", string="Manufactured By", store=True
    )
    device_protocol = fields.Char(
        related="device_model_id.model_protocol", string="Protocol", store=True
    )
    device_port = fields.Char(
        related="device_model_id.model_port", string="Port", store=True
    )
