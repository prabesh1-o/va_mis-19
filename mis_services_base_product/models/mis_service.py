from odoo import api, fields, models


class MisService(models.Model):
    _inherit = "mis.services"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    tax_mandatory = fields.Boolean(string="Tax Mandatory", default=False)
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        help="Select applicable tax for the service. "
        "The tax will be applied directly when quotation is made.",
    )
    total_price = fields.Monetary(
        string="Total Price", currency_field="company_currency_id",
    )

    def _set_product_product(self, service):
        service.product_product_id = (
            self.env["product.product"].search([("service_id", "=", service.id)]).id
        )

    def _create_product_template(self, services):
        for service in services:
            self.env["product.template"].create(
                {
                    "name": service.name,
                    "sale_ok": True,
                    "purchase_ok": False,
                    "detailed_type": "service",
                    "invoice_policy": "delivery",
                    "list_price": service.total_price,
                    "categ_id": self.env["product.category"]
                    .search([("name", "=", "Services")])
                    .id,
                    "service_id": service.id,
                }
            )
            self._set_product_product(service)

    def _update_product_template(self):
        for service in self:
            service.product_product_id.write(
                {
                    "name": service.name,
                    "list_price": service.total_price,
                    "taxes_id": [(6, 0, service.tax_ids.ids)],
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._create_product_template(res)
        return res

    def write(self, vals):
        res = super().write(vals)
        if (
            vals.get("name", False)
            or vals.get("product_ids", False)
            or vals.get("tax_ids", False)
        ):
            self._update_product_template()
        return res

    def unlink(self):
        for service in self:
            product_template = self.env["product.template"].browse(
                service.product_product_id.product_tmpl_id.id
            )
            if product_template:
                product_template.unlink()
        return super().unlink()
