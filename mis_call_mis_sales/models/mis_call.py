from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisCall(models.Model):
    _inherit = "mis.call"

    sale_ids = fields.One2many("sale.order", "call_id", string="Sale id")
    category = fields.Selection(
        selection_add=[("quotation", "Quotation")],
        ondelete={"quotation": "set default",},
    )
    commitment_date = fields.Datetime(string="Delivery Date")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    has_quotation = fields.Boolean(compute="_compute_has_quotation")

    order_line_ids = fields.One2many(
        "call.order.line", "call_id", string="Services", tracking=True
    )

    @api.depends("sale_ids")
    def _compute_has_quotation(self):
        """
        Compute the 'has_quotation' field based on the existence of related sale orders.

        If there are any sale orders associated with the call, sets 'has_quotation' to True.
        Otherwise, sets 'has_quotation' to False.
        """
        for call in self:
            if call.sale_ids:
                call.has_quotation = True
            else:
                call.has_quotation = False

    def action_create_sale_order(self):
        """
        Create a sale order for the current call.

        This method creates a new sale order using the information from the call and its order lines.
        The sale order is associated with the current call.

        Sale order fields populated:
        - partner_id: Customer associated with the call.
        - user_id: User responsible for the call.
        - commitment_date: Delivery date from the call.
        - company_id: Company of the call.
        - date_order: Current date and time.
        - pricelist_id: Default pricelist with the highest sequence.
        - order_line: Order lines created from the call's service order lines.
        """
        for call in self:
            pricelist_id = (
                self.env["product.pricelist"].search([("sequence", "=", 1)]).id
            )
            user_id = call.user_id.user_id.id
            sale_order = self.env["sale.order"].create(
                {
                    "partner_id": call.customer_id.id,
                    "user_id": user_id,
                    "commitment_date": call.commitment_date,
                    "company_id": call.company_id.id,
                    "date_order": fields.Datetime.now(),
                    "pricelist_id": pricelist_id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.service_id.product_product_id.id,
                                "product_uom_qty": line.quantity,
                                "price_unit": line.final_price,
                                "renewal_price": line.renewal_price,
                            },
                        )
                        for line in call.order_line_ids
                    ],
                }
            )
            call.sale_ids = [(4, sale_order.id)]

    def action_view_quotation(self):
        """
        View the quotation associated with the current call.

        This method returns an action that opens the form view of the sale order quotation
        related to the call. The view is set to 'form' mode and the sale order is loaded
        based on the 'call_id' field.

        Returns:
            dict: An action dictionary for viewing the quotation in form view.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale.action_quotations_with_onboarding"
        )
        action["context"] = {"search_default_call_id": self.id}
        action["view_mode"] = "form"
        action["res_id"] = self.sale_ids.id
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
                - order_line_ids
                - commitment_date
                - customer_id
                - user_id
            The error message instructs the user that they cannot change the category and
            suggests discarding the changes or creating a new call record.
        """
        fields_to_check = [
            self.order_line_ids,
            self.commitment_date,
            self.customer_id,
            self.user_id,
        ]
        if any(fields_to_check):
            raise ValidationError(
                _(
                    "You cannot change the category now. \nDiscard the changes or create a new call record."
                )
            )
