from odoo import _, http
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request


class PortalAccount(portal.CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        """
        Prepare and return values for the home portal dashboard.

        Adds the count of devices for the current user's partner if requested in the counters.
        """
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if "device_count" in counters:
            device_count = request.env["mis.device"].search_count(
                [("customer_id", "in", [partner.id])]
            )

            if device_count:
                values["device_count"] = device_count
            else:
                values["device_count"] = ""
        return values

    def _get_device_searchbar_sortings(self):
        """
        Return a dictionary of sorting options for the device portal view.
        """
        return {
            "expiry_date": {"label": _("Expiry Date"), "order": "expiration_time asc",},
            "installation_date": {
                "label": _("Installation Date"),
                "order": "installed_date asc",
            },
        }

    def _prepare_device_portal_rendering_values(
        self, page=1, device_page=False, sortby=None, **kwargs
    ):
        """
        Prepare and return values used for rendering the device portal page.

        Includes pagination, sorting, and filtering for devices related to the current partner.
        """
        if not sortby:
            sortby = "expiry_date"
        Device = request.env["mis.device"]
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        if device_page:
            url = "/my/devices"
            domain = [("customer_id", "in", [partner.id])]
        searchbar_sortings = self._get_device_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"]
        pager_values = portal_pager(
            url=url,
            total=Device.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={"sortby": sortby},
        )
        devices = Device.search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        values.update(
            {
                "devices": devices.sudo() if device_page else Device,
                "page_name": "devices",
                "pager": pager_values,
                "default_url": url,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return values

    @http.route(
        ["/my/devices", "/my/devices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_devices(self, **kwargs):
        """
        Render the 'My Devices' portal page for the logged-in user.

        Displays a paginated list of devices associated with the user's partner.
        """
        values = self._prepare_device_portal_rendering_values(
            device_page=True, **kwargs
        )
        request.session["my_devices"] = values["devices"].ids[:100]
        return request.render("mis_customer_portal.portal_my_devices", values)
