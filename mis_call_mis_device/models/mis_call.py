from odoo import fields, models


class MisCall(models.Model):
    _inherit = "mis.call"

    device_ids = fields.Many2many("mis.device", tracking=True,)
