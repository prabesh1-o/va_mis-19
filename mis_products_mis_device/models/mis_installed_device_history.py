from odoo import fields, models


class MisInstalledDeviceHistory(models.Model):
    _inherit = "mis.installed.device.history"

    model_id = fields.Many2one(
        related="device_id.device_model_id", string="Model", readonly=True
    )
    product_id = fields.Many2one(
        related="device_id.product_id", string="Product", readonly=True
    )
    manufacturer = fields.Many2one(
        related="device_id.manufacturer", string="Manufacturer", readonly=True
    )
    port = fields.Char(related="device_id.device_port", string="Port", readonly=True)
