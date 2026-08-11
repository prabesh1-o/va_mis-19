from odoo import fields, models


class MisDeviceRenewal(models.Model):
    _inherit = "mis.device.renewal"

    service_id = fields.Many2one(
        "mis.services", related="device_ids.service_id", store=True
    )
