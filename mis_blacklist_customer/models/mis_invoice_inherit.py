from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def validate_blacklist(self):
        for record in self:
            record.partner_id.validate_blacklist_customer()
