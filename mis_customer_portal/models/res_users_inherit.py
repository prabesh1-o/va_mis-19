from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    geomate_username = fields.Char(string="geomate username")
    geomate_password = fields.Char(string="geomate password")
