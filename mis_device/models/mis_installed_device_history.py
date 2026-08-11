from odoo import fields, models


class MisInstalledDeviceHistory(models.Model):
    _name = "mis.installed.device.history"
    _description = "MIS Installed Devices History"

    is_active = fields.Boolean(default=True, string="Active")
    device_id = fields.Many2one("mis.device", string="Device")
    customer_id = fields.Many2one("res.partner", string="Customer")
