from odoo import api, models


class MisDeviceWarranty(models.Model):
    _inherit = "mis.warranty"

    @api.onchange("customer_id")
    @api.depends("customer_id")
    def validate_blacklist(self):
        for record in self:
            record.customer_id.validate_blacklist_customer()
