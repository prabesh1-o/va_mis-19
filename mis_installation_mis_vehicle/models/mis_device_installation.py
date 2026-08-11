from odoo import fields, models


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    vehicle_id = fields.Many2one(
        "mis.vehicle", string="Vehicle No.", domain="[('device_ids','=',False)]"
    )
