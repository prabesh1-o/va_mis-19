from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    renewal_price = fields.Monetary(
        currency_field="currency_id", string="Renewal Price"
    )
    discount_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_discount_price", store=True,
    )
    invoice_status = fields.Selection(
        selection_add=[("partially_invoiced", "Partially Invoiced"),],
        ondelete={"partially_invoiced": "cascade",},
    )

    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self:
            # Set invoice status to partially invoiced if total qty
            # of product is greater than delivered qty(equal to
            # invoiced qty) and delivered is greater than 0.
            if (
                line.qty_delivered > 0
                and line.qty_delivered == line.qty_invoiced
                and line.product_id.invoice_policy == "delivery"
                and line.product_uom_qty > line.qty_delivered
            ):
                line.invoice_status = "partially_invoiced"
        return res

    @api.depends(
        "price_unit", "price_reduce_taxexcl", "product_uom_qty", "discount",
    )
    def _compute_discount_price(self):
        """
        Compute the discount amount based on the difference between unit
        price and reduced price excluding taxes, multiplied by the quantity,
        if a discount is applied.
        """
        for line in self:
            line.discount_amount = (
                # price_reduce_taxexcl is the price for a unit excluding tax
                (line.price_unit - line.price_reduce_taxexcl) * line.product_uom_qty
                if line.discount
                else 0.0
            )

    @api.onchange("price_total")
    def _compute_unit_price(self):
        """
        Calculates unit price of line of sale order if total price of line is
        changed depending upon discount and tax applied.
        """
        for line in self:
            if line.tax_ids and not line.discount:
                untaxed_amt = line.price_total / (1 + (line.tax_ids[:1].amount / 100))
                line.price_unit = untaxed_amt / line.product_uom_qty
            elif line.tax_ids and line.discount:
                untaxed_amt = line.price_total / (1 + (line.tax_ids[:1].amount / 100))
                undisc_amt = untaxed_amt / (1 - (line.discount / 100))
                line.price_unit = undisc_amt / line.product_uom_qty
            elif not line.tax_ids and line.discount:
                undisc_amt = line.price_total / (1 - (line.discount / 100))
                line.price_unit = undisc_amt / line.product_uom_qty
            else:
                line.price_unit = line.price_total / line.product_uom_qty
