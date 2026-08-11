from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_blacklist = fields.Boolean(
        default=False, string="Blacklist Customer", tracking=True
    )
    blacklist_ids = fields.One2many(
        "mis.blacklist.customer", "customer_id", string="Blacklist Requests"
    )

    def btn_request_blacklist(self):
        """
        Initiates a new blacklist request for a customer if no active requests exist.
        Raises an error if a non-rejected or non-approved blacklist request is already present
        or if customer is already blacklisted.
        Opens a form view to create the blacklist request.
        """
        for customer in self:
            if customer.is_blacklist:
                raise UserError(_("The customer is already blacklisted!"))
            elif any(
                blacklist.stage not in ["rejected", "approved"]
                for blacklist in customer.blacklist_ids
            ):
                raise UserError(_("The blacklist request is already created!"))
            return {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "mis.blacklist.customer",
                "target": "new",
                "context": {
                    "default_customer_id": customer.id,
                    "default_request_date": fields.Date.today(),
                    "default_requested_by": self.env.user.employee_id.id,
                },
            }

    def validate_blacklist_customer(self):
        for customer in self:
            if customer.is_blacklist:
                raise UserError(
                    _("Cannot create a record for blacklisted customer: %s.")
                    % customer.name
                )
