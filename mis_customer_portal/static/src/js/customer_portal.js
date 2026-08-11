/** @odoo-module **/

import publicWidget from "web.public.widget";
import rpc from "web.rpc";

publicWidget.registry.CustomerPortal = publicWidget.Widget.extend({
  selector: ".o_portal_wrap",
  events: {
    "click .js_open_customer_portal": "_onClickPortal",
  },

  _onClickPortal: function() {
    const errorPlaceholder = document.querySelector(".portal-error-placeholder");
    if (errorPlaceholder) errorPlaceholder.innerHTML = "";

    rpc
      .query({
        route: "/my/portal",
        params: {},
      })
      .then(({domain, username, password, missing_credentials}) => {
        if (missing_credentials) {
          if (errorPlaceholder) {
            errorPlaceholder.innerHTML = `<div class="alert alert-danger">Missing credentials. Please add from portal settings.</div>`;
          }
          return;
        }

        if (domain && username && password) {
          const apiUrl = `${domain}/login.php?username=${username}&password=${password}&mobile=false`;
          window.open(apiUrl, "_blank");
        }
      })
      .catch(err => {
        console.error("RPC call failed:", err);
        if (errorPlaceholder) {
          errorPlaceholder.innerHTML = `<div class="alert alert-danger">An error occurred while contacting the portal.</div>`;
        }
      });
  },
});
