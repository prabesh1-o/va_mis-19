import requests
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class PortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "customer_portal_count" in counters:
            values["customer_portal_count"] = ""
        return values

    @http.route(
        ["/my/portal"], type="json", auth="user", website=True,
    )
    def portal_customer(self, **kwargs):
        SERVER_DOMAIN = (
            request.env["ir.config_parameter"].sudo().get_param("mis.mis_server_domain")
        )
        if not SERVER_DOMAIN:
            return http.Response(
                "<h3>Server domain not configured.</h3>", content_type="text/html"
            )
        current_user = request.env.user
        USERNAME = current_user.geomate_username
        PASSWORD = current_user.geomate_password
        if not USERNAME or not PASSWORD:
            return {"missing_credentials": True}
        return {"domain": SERVER_DOMAIN, "username": USERNAME, "password": PASSWORD}

    @http.route(
        "/my/portal/security",
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def portal_security(self, **kwargs):
        success = False
        failure = False
        error_message = None

        if request.httprequest.method == "POST":
            username = kwargs.get("username")
            password = kwargs.get("password")

            server_domain = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.mis_server_domain")
            )
            if not server_domain:
                return http.Response(
                    "<h3>Server domain not configured.</h3>", content_type="text/html"
                )

            if username and password:
                login_url = f"{server_domain}/login.php?username={username}&password={password}&mobile=false"
                try:
                    response = requests.get(login_url, timeout=5)
                    if (
                        response.status_code == 200
                        and not response.text == "ERROR_USERNAME_PASSWORD_INCORRECT"
                    ):
                        request.env.user.sudo().write(
                            {"geomate_username": username, "geomate_password": password}
                        )
                        success = True
                    else:
                        failure = True
                        error_message = (
                            "Portal credentials do not match. Please try again."
                        )

                except requests.exceptions.RequestException as e:
                    failure = True
                    error_message = f"Server connection failed: {str(e)}"

        return request.render(
            "mis_customer_portal.customer_portal_my_security",
            {"success": success, "failure": failure, "error_message": error_message,},
        )
