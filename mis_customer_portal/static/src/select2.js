odoo.define("mis_customer_portal.ticket_portal_form_view", function(require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  publicWidget.registry.WebsiteCustomerContactRequestForm = publicWidget.Widget.extend({
    selector: ".ticket_portal_form",
    start: function() {
      var self = this;
      setTimeout(function() {
        self.$("select.select2").select2({
          allowClear: true,
          width: "100%",
        });
      }, 100);
      return this._super.apply(this, arguments);
    },
  });
});
