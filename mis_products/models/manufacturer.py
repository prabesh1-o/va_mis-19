from odoo import fields, models


class MisManufacturer(models.Model):
    _name = "mis.manufacturer"
    _description = "MIS Manufacturers"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    address = fields.Char(string="Address")
    contact_no = fields.Char(string="Contact No.")
    email = fields.Char(string="E-mail")
    website = fields.Char(string="Website")
    state = fields.Selection(
        selection=[("active", "Active"), ("inactive", "Inactive")],
        string="Status",
        required=True,
        default="active",
        tracking=True,
    )
    supplier_id = fields.Many2one("mis.supplier")
