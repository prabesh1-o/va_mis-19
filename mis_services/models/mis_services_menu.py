from odoo import fields, models


class MisServicesMenu(models.Model):
    _name = "mis.services.menu"
    _description = "Mis Services Menu"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    tag_ids = fields.Many2many("mis.services.menu.tags", string="Tags")
    service_ids = fields.One2many("mis.services", "service_menu_id")
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    service_count = fields.Integer(
        compute="_compute_service_count", string="Service Count"
    )

    def _compute_service_count(self):
        for menu in self:
            menu.service_count = len(menu.service_ids)


class MisServicesMenuTags(models.Model):
    _name = "mis.services.menu.tags"
    _description = "Mis Service Menu Tags"

    name = fields.Char(string="name", required=True)
    color = fields.Char(string="color")
