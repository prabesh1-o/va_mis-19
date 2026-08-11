from odoo import api, fields, models


class MisProduct(models.Model):
    _inherit = "mis.product"

    product_product_id = fields.Many2one("product.product")
    detailed_type = fields.Selection(
        [("consu", "Consumable"), ("product", "Storable Product")], required=True
    )

    def _set_product_product(self, product):
        product.product_product_id = (
            self.env["product.product"].search([("mis_product_id", "=", product.id)]).id
        )

    def _create_product_template(self, products):
        for product in products:
            self.env["product.template"].create(
                {
                    "name": product.name,
                    "sale_ok": False,
                    "purchase_ok": True,
                    "detailed_type": product.detailed_type,
                    "list_price": (
                        product.discounted_price
                        if product.discounted_price
                        else product.price
                    ),
                    "categ_id": self.env["product.category"]
                    .search([("name", "=", "All")], limit=1)
                    .id,
                    "mis_product_id": product.id,
                }
            )
            self._set_product_product(product)

    def _update_product_template(self):
        for product in self:
            product.product_product_id.write(
                {
                    "name": product.name,
                    "lst_price": (
                        product.discounted_price
                        if product.discounted_price
                        else product.price
                    ),
                    "purchase_ok": True,
                    "detailed_type": product.detailed_type,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._create_product_template(res)
        return res

    def write(self, vals):
        res = super().write(vals)
        if any(
            field in vals
            for field in [
                "name",
                "price",
                "discounted_price",
                "discount_percentage",
                "detailed_type",
            ]
        ):
            self._update_product_template()
        return res

    def unlink(self):
        for product in self:
            product.product_product_id.unlink()
        return super().unlink()
