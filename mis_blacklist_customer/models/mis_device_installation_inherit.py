from odoo import api, models


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    @api.onchange("customer_id")
    @api.depends("customer_id")
    def validate_blacklist(self):
        for record in self:
            record.customer_id.validate_blacklist_customer()
