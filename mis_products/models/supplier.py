from odoo import models


class MisSupplier(models.Model):
    _name = "mis.supplier"
    _description = "MIS Suppliers"
    _inherit = "mis.manufacturer"
