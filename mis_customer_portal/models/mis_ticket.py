from odoo import fields, models


class MisTicket(models.Model):
    _name = "mis.ticket"
    _inherit = ["mis.ticket", "portal.mixin"]

    access_url = fields.Char(compute="_compute_access_url")

    def _compute_access_url(self):
        for ticket in self:
            ticket.access_url = f"/my/tickets/{ticket.id}"

    def _get_portal_return_action(self):
        self.ensure_one()
        return self.env.ref("mis_tickets.action_view_all_ticket_views")
