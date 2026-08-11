from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CallOrderLine(models.Model):
    _name = "call.order.line"
    _description = "Order lines for mis call"

    call_id = fields.Many2one("mis.call")
    company_currency_id = fields.Many2one(related="call_id.company_currency_id")
    service_price = fields.Monetary(
        compute="_compute_service_price",
        currency_field="company_currency_id",
        string="Actual Price",
        store=True,
    )
    discount_percentage = fields.Float(string="Discount(%)")
    final_price = fields.Monetary(
        compute="_compute_final_price",
        currency_field="company_currency_id",
        string="Price",
        store=True,
    )
    offered_price = fields.Monetary(
        currency_field="company_currency_id", string="Offered Price"
    )
    quantity = fields.Integer(string="Quantity", default=1)
    amount = fields.Monetary(
        compute="_compute_amount",
        currency_field="company_currency_id",
        string="Amount",
        store=True,
    )
    service_id = fields.Many2one("mis.services", string="Service")

    renewal_price = fields.Monetary(
        currency_field="company_currency_id", string="Renewal Price"
    )

    @api.depends("service_id")
    def _compute_service_price(self):
        """
        Computes the actual service price based on the selected service.

        If a service is selected, the service price is set to the total price of the service.
        """
        for line in self:
            if line.service_id:
                line.service_price = line.service_id.total_price

    @api.depends("quantity", "final_price")
    def _compute_amount(self):
        """
        Computes the total amount for the order line.

        The total amount is calculated by multiplying the final price by the quantity.
        If either the final price or quantity is not set, the amount is set to 0.
        """
        for line in self:
            if line.final_price and line.quantity:
                line.amount = line.final_price * line.quantity
            else:
                line.amount = 0

    @api.depends("discount_percentage", "service_price")
    def _compute_final_price(self):
        """
        Computes the final price for each service line based on the discount percentage and service price.

        The method iterates over each service line, applying a discount to the service price if a valid discount
        percentage is provided. The discount percentage must be between 0 and 100 (inclusive). If the discount
        percentage is outside this range, a UserError is raised. If either the discount percentage or service
        price is not provided, the final price is set to the service price.

        """
        for service_line in self:
            discount_percent = service_line.discount_percentage
            if discount_percent and service_line.service_price:
                if 0 < discount_percent <= 100:
                    service_line.final_price = (
                        service_line.service_price
                        - (discount_percent / 100) * service_line.service_price
                    )
                else:
                    raise UserError(
                        _("Discount percentage cannot be less than 0 or more than 100.")
                    )
            else:
                service_line.final_price = service_line.service_price
