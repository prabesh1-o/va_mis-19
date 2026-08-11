from odoo import api, fields, models


class SaleOrderLineUpdateWizard(models.TransientModel):
    _name = "sale.order.line.update.wizard"
    _description = "Sale Order Line Edit Wizard"
    name = "sale_order_id"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", readonly=True)
    line_ids = fields.One2many(
        "sale.order.line.update.wizard.line",
        "wizard_id",
        readonly=False,
        string="Order Lines",
        compute="_compute_lines",
        store=True,
    )

    @api.depends("sale_order_id")
    def _compute_lines(self):
        for wiz in self:
            wiz.write(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "sale_order_line_id": order_line.id,
                                "price_unit": order_line.price_unit,
                                "discount": order_line.discount,
                                "qty_delivered": order_line.qty_delivered,
                                "qty_cancelled": order_line.qty_cancelled,
                            },
                        )
                        for order_line in wiz.sale_order_id.order_line
                    ]
                }
            )

    def apply_changes(self):
        for line in self.line_ids:
            sale_order_line = line.sale_order_line_id
            if sale_order_line:
                sale_order_line.write(
                    {
                        "product_uom_qty": line.product_uom_qty,
                        "price_unit": line.price_unit,
                        "discount": line.discount,
                        "qty_delivered": line.qty_delivered,
                        "qty_cancelled": line.qty_cancelled,
                    }
                )
        return {"type": "ir.actions.act_window_close"}


class SaleOrderLineUpdateWizardLine(models.TransientModel):
    _name = "sale.order.line.update.wizard.line"
    _description = "Sale Order Line Edit Wizard Line"

    wizard_id = fields.Many2one(
        "sale.order.line.update.wizard", string="Wizard Reference"
    )
    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    product_uom_qty = fields.Float(
        string="Quantity", related="sale_order_line_id.product_uom_qty"
    )
    price_unit = fields.Float(string="Unit Price")
    qty_delivered = fields.Float(string="Quantity Delivered")
    qty_cancelled = fields.Float(string="Quantity Cancelled")
    discount = fields.Float(string="Discount")
