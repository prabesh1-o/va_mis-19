from odoo import api, models


class MisDeviceRenewal(models.Model):
    _inherit = "mis.device.renewal"

    @api.onchange("customer_ids")
    @api.depends("customer_ids")
    def validate_blacklist(self):
        for record in self:
            record.customer_ids.validate_blacklist_customer()

    @api.model
    def create(self, vals):
        if "customer_ids" in vals:
            partner_ids = []
            for customer_ids in vals.get("customer_ids"):
                if self.env.context.get("scheduler"):
                    # customer_ids is in format (4, id)
                    partner_ids.append(customer_ids[1])
                else:
                    # customer_ids is in format [6, 0, [ids]]
                    partner_ids = customer_ids[2]
            customers = self.env["res.partner"].browse(partner_ids)
            customers.validate_blacklist_customer()
        return super().create(vals)

    def write(self, vals):
        if "customer_ids" in vals:
            customer_ids = (
                vals.get("customer_ids")[0][2] if vals.get("customer_ids") else []
            )
            customers = self.env["res.partner"].browse(customer_ids)
            customers.validate_blacklist_customer()
        return super().write(vals)
