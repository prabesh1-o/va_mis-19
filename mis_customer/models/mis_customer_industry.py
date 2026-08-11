from odoo import fields, models


class MisCustomerIndustry(models.Model):
    _name = "mis.customer.industry"
    _description = "MIS Customer Industry"

    name = fields.Char(string="Name", required=True)
    prefix = fields.Char(string="Prefix", required=True)
