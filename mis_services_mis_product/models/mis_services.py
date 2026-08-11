from odoo import api, fields, models


class MisServices(models.Model):
    _inherit = "mis.services"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    product_ids = fields.Many2many("mis.product", string="Products")
    total_product_info = fields.Html(
        compute="_compute_total_product_info", sanitize=True
    )
    total_product_count = fields.Integer(
        compute="_compute_total_product_count", string="Total Product"
    )
    total_price = fields.Monetary(
        string="Total Price",
        currency_field="company_currency_id",
        compute="_compute_service_total_price",
        store=True,
    )

    @api.depends("product_ids")
    def _compute_total_product_info(self):
        for service in self:
            product_html = ""
            for product_type in service.product_ids.product_type:
                product_html += f"""
                    <li>{product_type.name}</li>
                """
            service.total_product_info = product_html

    def _compute_total_product_count(self):
        for service in self:
            service.total_product_count = len(service.product_ids)

    @api.depends("product_ids.price_subtotal")
    def _compute_service_total_price(self):
        for service in self:
            service.total_price = sum(service.product_ids.mapped("price_subtotal"))
