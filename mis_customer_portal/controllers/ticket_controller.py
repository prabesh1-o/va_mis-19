from odoo import _, http
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalAccount(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        """
        Prepare and return values for the home portal dashboard.

        Adds the ticket count for the current user's partner if requested in the counters.
        """
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if "ticket_count" in counters:
            ticket_count = (
                request.env["mis.ticket"]
                .sudo()
                .search_count([("customer_id", "=", partner.id)])
            )
            if ticket_count:
                values["ticket_count"] = ticket_count
            else:
                values["ticket_count"] = ""
        return values

    def _get_ticket_searchbar_sortings(self):
        """
        Return a dictionary of sorting options for the ticket portal view.
        """
        return {
            "ticket_id": {"label": _("Ticket"), "order": "ticket_id desc",},
            "vehicle": {"label": _("Vehicle"), "order": "vehicle_id asc",},
        }

    def _prepare_ticket_portal_rendering_values(
        self, page=1, ticket_page=False, sortby=None, **kwargs
    ):
        """
        Prepare and return values used for rendering the ticket portal page.

        Includes pagination, sorting, and filtering for tickets related to the current partner.
        """
        if not sortby:
            sortby = "ticket_id"
        Ticket = request.env["mis.ticket"]
        user = request.env.user
        partner = user.partner_id
        values = self._prepare_portal_layout_values()
        if ticket_page:
            url = "/my/tickets"
            domain = [
                ("customer_id", "=", partner.id),
            ]
        searchbar_sortings = self._get_ticket_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        pager_values = portal_pager(
            url=url,
            total=Ticket.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={"sortby": sortby},
        )
        tickets = Ticket.sudo().search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        values.update(
            {
                "tickets": tickets.sudo() if ticket_page else Ticket,
                "page_name": "tickets",
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return values

    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(self, **kwargs):
        """
        Render the 'My Tickets' portal page for the logged-in user.
        """
        values = self._prepare_ticket_portal_rendering_values(
            ticket_page=True, **kwargs
        )
        notification = request.session.pop("portal_notification", None)
        values["notification"] = notification
        request.session["my_tickets"] = values["tickets"].ids[:100]
        return request.render("mis_customer_portal.portal_my_tickets", values)

    @http.route(
        ["/my/tickets/<int:ticket_id>"], type="http", auth="public", website=True
    )
    def portal_ticket_page(
        self, ticket_id, access_token=None, **kw,
    ):
        """
        Render the details page for a specific ticket.

        Redirects to the main portal page if access is denied or the ticket is missing.
        """
        try:
            ticket_sudo = self._document_check_access(
                "mis.ticket", ticket_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        created_datetime = ticket_sudo.create_date.strftime("%Y-%m-%d %H:%M:%S")
        backend_url = (
            f"/web#model={ticket_sudo._name}"
            f"&id={ticket_sudo.id}"
            f"&action={ticket_sudo._get_portal_return_action().id}"
            f"&view_type=form"
        )
        values = {
            "ticket": ticket_sudo,
            "page_name": "ticket_id",
            "created_datetime": created_datetime,
            "report_type": "html",
            "backend_url": backend_url,
        }
        return request.render("mis_customer_portal.ticket_portal_template", values)

    @http.route("/my/ticket/form", type="http", auth="public", website=True)
    def open_ticket_form(self, **kw):
        """
        Render the ticket submission form page for the user.

        Provides a list of the user's devices, vehicles, and ticket tags.
        """
        user = request.env.user
        partner = user.partner_id
        values = self._prepare_portal_layout_values()
        devices = (
            request.env["mis.device"].sudo().search([("customer_id", "=", partner.id)])
        )
        vehicles = (
            request.env["mis.vehicle"].sudo().search([("customer_id", "=", partner.id)])
        )
        tags = request.env["mis.ticket.tags"].sudo().search([])
        values = {
            "devices": devices,
            "page_name": "ticket_form",
            "vehicles": vehicles,
            "tags": tags,
        }
        return request.render("mis_customer_portal.ticket_portal_form_view", values)

    @http.route(
        "/my/ticket/submit", type="http", auth="public", website=True, methods=["POST"]
    )
    def create_ticket(self, **kw):
        """
        Handle the submission of a new ticket via the portal.

        Creates a ticket with the submitted form data and redirects the user to the ticket list.
        """
        tag_ids = [int(t) for t in request.httprequest.form.getlist("tags")]
        menu_id = (
            request.env["mis.ticket.menu"]
            .sudo()
            .search([("is_complain", "=", True)], limit=1)
            .id
        )
        stage_id = (
            request.env["mis.ticket.stage"]
            .sudo()
            .search([("sequence", "=", 0), ("ticket_menu_ids", "=", menu_id)], limit=1)
            .id
        )
        ticket = (
            request.env["mis.ticket"]
            .sudo()
            .create(
                {
                    "customer_id": request.env.user.partner_id.id,
                    "vehicle_id": int(kw.get("vehicle")),
                    "description": kw.get("description"),
                    "tag_ids": [(6, 0, tag_ids)],
                    "ticket_menu_id": menu_id,
                    "stage_id": stage_id,
                    "priority": kw.get("priority"),
                }
            )
        )
        request.session["portal_notification"] = {
            "type": "success",
            "message": f"Ticket {ticket.ticket_id} opened successfully!",
        }
        return request.redirect("/my/tickets")
