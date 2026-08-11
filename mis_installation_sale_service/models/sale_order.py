from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_installation_order(self):
        for order in self:
            if order.partner_id and order.order_line:
                order._validate_delivered_quantity()
                order._validate_contains_installable_line()
                ordered_quantity = len(
                    order.order_line.installation_line_ids.filtered(
                        lambda x: x.state != "canceled"
                    )
                )
                if order.installation_ids:
                    if ordered_quantity < len(order.order_line):
                        order._create_installation_order(ordered_quantity)
                    else:
                        raise UserError(
                            _("All Installation orders are already created.")
                        )
                else:
                    order._create_installation_order(ordered_quantity)
            else:
                raise UserError(
                    _(
                        "Partner and Order lines are required to create installation order"
                    )
                )

    def _create_installation_order(self, ordered_quantity):
        self.write(
            {
                "installation_ids": [
                    (
                        0,
                        0,
                        {
                            "customer_id": self.partner_id.id,
                            "date_deadline": self.commitment_date,
                            "sale_order_id": self.id,
                            "installation_line_ids": [
                                (0, 0, self._prepare_installation_lines(line))
                                for line in self.order_line
                                for _ in range(
                                    int(line.product_uom_qty - ordered_quantity)
                                )
                                if line.product_template_id.service_id.is_installable
                            ],
                        },
                    )
                ]
            }
        )

    def _prepare_installation_lines(self, line):
        return {
            "service_id": line.product_template_id.service_id.id,
            "installation_price": line.price_reduce_taxexcl,
            "has_tax_installation": bool(line.tax_id),
            "renewal_price": line.renewal_price,
        }

    def _validate_delivered_quantity(self):
        if sum(self.order_line.mapped("qty_delivered")) == sum(
            self.order_line.mapped("product_uom_qty")
        ):
            raise UserError(
                _(
                    "Every service has already been delivered, You cannot create Installation Order."
                )
            )

    def _validate_contains_installable_line(self):
        if not any(
            self.order_line.product_template_id.service_id.mapped("is_installable")
        ):
            raise UserError(_("None of the order lines contains installable services."))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_cancelled = fields.Float(string="Cancelled", readonly=True)
    service_is_installable = fields.Boolean(compute="_compute_is_installable")

    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self:
            if (
                line.qty_cancelled > 0
                and line.product_uom_qty == line.qty_invoiced + line.qty_cancelled
            ):
                line.invoice_status = "invoiced"
        return res

    def _compute_is_installable(self):
        for line in self:
            line.service_is_installable = (
                line.product_template_id.service_id.is_installable
            )
