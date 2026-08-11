from odoo import fields, models


class MisServices(models.Model):
    _inherit = "mis.services"

    product_product_id = fields.Many2one("product.product")
    sale_unit_count = fields.Float(
        related="product_product_id.sales_count", readonly=True
    )
    uom_name = fields.Char(related="product_product_id.uom_name", readonly=True)
    sellable_units = fields.Integer(
        string="Sellable Units", compute="_compute_sellable_units"
    )

    def action_view_mis_services_sold(self):
        self.ensure_one()
        return self.product_product_id.product_tmpl_id.action_view_sales()

    def _compute_sellable_units(self):
        for service in self:
            purchasable = []
            for product in service.product_ids:
                if (
                    product.product_product_id.type == "product"
                    and product.is_product
                ):
                    units = product.product_product_id.qty_available // product.quantity
                    purchasable.append(units)
            if purchasable:
                service.sellable_units = int(min(purchasable))
            else:
                service.sellable_units = 0

    def action_sellable(self):
        self.ensure_one()
        self._compute_sellable_units()
        return True
