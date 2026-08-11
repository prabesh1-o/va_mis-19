from odoo import fields, models


class MisTicket(models.Model):
    _inherit = "mis.ticket"

    call_id = fields.Many2one("mis.call", string="Call Id.")
