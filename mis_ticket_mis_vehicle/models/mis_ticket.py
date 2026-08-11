from odoo import fields, models


class MisTicket(models.Model):
    _inherit = "mis.ticket"

    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle")
    device_imei = fields.Char(
        related="vehicle_id.device_ids.imei_no", string="Device", store=True
    )
