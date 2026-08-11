from odoo import api, models


class MisTicket(models.Model):
    _inherit = "mis.ticket"

    @api.onchange("customer_id")
    @api.depends("customer_id")
    def validate_blacklist(self):
        for record in self:
            record.customer_id.validate_blacklist_customer()
