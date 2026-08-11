from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisCall(models.Model):
    _inherit = "mis.call"

    renewal_ids = fields.One2many("mis.device.renewal", "call_id", string="Renewal id")
    category = fields.Selection(
        selection_add=[("renewal", "Renewal")], ondelete={"renewal": "set default",},
    )

    renewal_tag_ids = fields.Many2many(
        "mis.device.renewal.tags", string="Renewal tags", tracking=True
    )
    has_renewal = fields.Boolean(compute="_compute_has_renewal", string="Renewal")
    device_ids = fields.Many2many("mis.device", tracking=True,)

    @api.depends("renewal_ids")
    def _compute_has_renewal(self):
        """
        Compute the has_renewal field based on the presence of renewal_ids.

        This method is a compute method for the has_renewal field. It sets
        has_renewal to True if there are any related renewal_ids, otherwise it
        sets it to False.
        """
        for call in self:
            if call.renewal_ids:
                call.has_renewal = True
            else:
                call.has_renewal = False

    def action_create_renewal(self):
        """
        Create a renewal record for the current call.

        This method creates a new mis.device.renewal record with the details
        from the current call. It populates the renewal with customer, tags,
        employee, and device information from the call. The created renewal
        is then linked to the call through the renewal_ids field.
        """
        for call in self:
            renewal_id = self.env["mis.device.renewal"].create(
                {
                    "customer_ids": call.customer_id,
                    "tag_ids": call.renewal_tag_ids,
                    "employee_ids": call.user_id,
                    "device_ids": [
                        (
                            0,
                            0,
                            {
                                "imei_no": line.imei_no,
                                "vehicle_id": line.vehicle_id.id,
                                "device_model_id": line.device_model_id.id,
                                "expiration_time": line.expiration_time,
                                "renewal_package_id": line.renewal_package_id.id,
                                "renewal_price": line.renewal_price,
                                "payment_date": line.payment_date,
                                "tax_id": line.tax_id.id,
                                "price_subtotal": line.price_subtotal,
                                "installed_date": line.installed_date,
                                "state": line.state,
                            },
                        )
                        for line in call.device_ids
                    ],
                }
            )
            call.renewal_ids = [(4, renewal_id.id)]

    def action_view_renewal(self):
        """
        View the renewal record associated with the current call.

        This method opens the form view of the associated mis.device.renewal
        record for the current call. It ensures only one call is selected,
        sets the context for the action, and restricts the view to form mode.
        Returns the action dictionary to open the renewal form view.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_device_renewal.mis_renewal_action"
        )
        action["context"] = {"search_default_call_id": self.id}
        action["view_mode"] = "form"
        action["res_id"] = self.renewal_ids.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action

    @api.onchange("category")
    def _onchange_category(self):
        """
        Handle changes to the 'category' field.

        This method is triggered when there is a change in the 'category' field of the record.
        It checks whether certain other fields in the record are set. If any of the specified
        fields are already populated, it raises a ValidationError to prevent changing the category.

        Raises:
            ValidationError: If any of the following fields are set:
                - user_id
                - renewal_tag_ids
                - device_ids
                - customer_id
            The error message instructs the user that they cannot change the category and
            suggests discarding the changes or creating a new call record.
        """
        fields_to_check = [
            self.user_id,
            self.renewal_tag_ids,
            self.device_ids,
            self.customer_id,
        ]
        if any(fields_to_check):
            raise ValidationError(
                _(
                    "You cannot change the category now. \nDiscard the changes or create a new call record."
                )
            )
