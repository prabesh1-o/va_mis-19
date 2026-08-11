from odoo import fields, models


class MisCall(models.Model):
    _inherit = "mis.call"

    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle No.",)
