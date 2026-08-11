from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fiscal_period_id = fields.Many2one("mis.fiscal.period", string="Fiscal Year")
