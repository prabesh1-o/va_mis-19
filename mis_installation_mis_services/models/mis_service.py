from odoo import fields, models


class MisService(models.Model):
    _inherit = "mis.services"

    is_installable = fields.Boolean(default=False, string="Installable")
    sop = fields.Html(string="SOP")
