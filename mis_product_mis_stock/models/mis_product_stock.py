from odoo import fields, models


class MisProduct(models.Model):
    _inherit = "mis.product"

    qty_available = fields.Float(
        related="product_product_id.qty_available", readonly=True
    )
    uom_name = fields.Char(
        related="product_product_id.product_tmpl_id.uom_name", readonly=True
    )
    nbr_moves_in = fields.Integer(
        related="product_product_id.nbr_moves_in", readonly=True
    )
    nbr_moves_out = fields.Integer(
        related="product_product_id.nbr_moves_out", readonly=True
    )
    purchased_product_qty = fields.Float(
        related="product_product_id.purchased_product_qty", readonly=True
    )

    forcasted_units = fields.Float(
        related="product_product_id.virtual_available", readonly=True
    )

    sales_count = fields.Float(related="product_product_id.sales_count", readonly=True)

    def action_view_mis_product_onhand(self):
        self.ensure_one()
        return self.product_product_id.action_open_quants()

    def action_view_mis_product_moves(self):
        self.ensure_one()
        return self.product_product_id.action_view_stock_move_lines()

    def action_view_mis_product_sold(self):
        self.ensure_one()
        return self.product_product_id.action_view_sales()

    def action_view_mis_product_purchase(self):
        self.ensure_one()
        return self.product_product_id.action_view_po()

    def action_view_mis_product_forcasted(self):
        self.ensure_one()
        return (
            self.product_product_id.product_tmpl_id.action_product_tmpl_forecast_report()
        )
