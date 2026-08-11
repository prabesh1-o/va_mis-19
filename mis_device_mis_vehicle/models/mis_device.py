from odoo import fields, models


class MisDevice(models.Model):
    _inherit = "mis.device"

    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle")
