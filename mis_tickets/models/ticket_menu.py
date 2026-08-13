import ast

from odoo import _, fields, models


class MisTicketMenu(models.Model):
    _name = "mis.ticket.menu"
    _description = "Mis Menu of All tickets"
    _order = "priority desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", tracking=True)
    date_start = fields.Date()
    date = fields.Date(string="End Date")
    user_id = fields.Many2one("res.users", string="Manager", tracking=True)
    active = fields.Boolean(default=True)
    is_completed = fields.Boolean(default=False)
    priority = fields.Selection(
        [("0", "Low"), ("1", "High"),], default="0", string="Priority",
    )
    tag_ids = fields.Many2many("mis.ticket.menu.tags", string="Tags")
    description = fields.Html(string="Description")
    sequence = fields.Integer()
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count", string="Task Count")
    ticket_ids = fields.One2many("mis.ticket", "ticket_menu_id", string="Ticket")

    def action_view_tickets(self):
        """
        Generate an action to view tickets with a customized view mode based on the menu.

        This method constructs an action to display all ticket views, adjusting the display
        name and context. If the current record is the 'Completed' menu, it sets the view mode
        to show the tree view by default along with kanban and form views. Otherwise, it
        defaults to kanban, tree, and form views.
        """
        action = (
            self.env["ir.actions.act_window"]
            .with_context({"active_id": self.id})
            ._for_xml_id("mis_tickets.action_view_all_ticket_views")
        )
        action["display_name"] = _("%(name)s", name=self.name)
        context = ast.literal_eval(action["context"].replace("active_id", str(self.id)))
        completed_menu = (
            self.env["mis.ticket.menu"]
            .with_context(active_test=False)
            .search([("is_completed", "=", True)], limit=1)
        )
        if self == completed_menu:
            action["views"] = [
                (False, "list"),
                (False, "kanban"),
                (False, "form"),
            ]
            action["view_mode"] = "list,kanban,form"
        else:
            action["view_mode"] = "kanban,list,form"
        action["context"] = context
        return action

    def _compute_ticket_count(self):
        for menu in self:
            menu.ticket_count = len(menu.ticket_ids)


class MisTicketMenuTags(models.Model):
    _name = "mis.ticket.menu.tags"
    _description = "Mis Tags for Ticket Menu"

    name = fields.Char(string="name", required=True)
    color = fields.Char(string="color")
