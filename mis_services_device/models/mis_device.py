from odoo import fields, models


class MisDevice(models.Model):
    _inherit = "mis.device"

    service_id = fields.Many2one("mis.services")
