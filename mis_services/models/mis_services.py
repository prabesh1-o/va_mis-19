from odoo import fields, models


class MisServices(models.Model):
    _name = "mis.services"
    _description = "Mis Services"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Service Name")
    tag_ids = fields.Many2many("mis.services.tags", string="Tags")
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    service_menu_id = fields.Many2one("mis.services.menu")
    product_product_id = fields.Many2one("product.product")

    active = fields.Boolean(default=True, string="Published")


class MisServicesTags(models.Model):
    _name = "mis.services.tags"
    _description = "Mis Tags for Ticket Menu"

    name = fields.Char(string="name", required=True)
    color = fields.Char(string="color")
