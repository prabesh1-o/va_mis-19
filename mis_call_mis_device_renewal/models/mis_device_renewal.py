from odoo import fields, models


class MisDeviceRenewal(models.Model):
    _inherit = "mis.device.renewal"

    call_id = fields.Many2one("mis.call", string="Call id")
