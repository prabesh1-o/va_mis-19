from odoo import api, fields, models


class MisServices(models.Model):
    _inherit = "mis.services"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    component_ids = fields.Many2many("mis.service.components", string="Components")
    total_component_info = fields.Html(
        compute="_compute_total_component_info", sanitize=True
    )
    total_component_count = fields.Integer(
        compute="_compute_total_component_count", string="Total component"
    )
    total_price = fields.Monetary(
        string="Total Price",
        currency_field="company_currency_id",
        compute="_compute_service_total_price",
        store=True,
    )

    @api.depends("component_ids")
    def _compute_total_component_info(self):
        for service in self:
            component_html = ""
            for component_type in service.component_ids.component_type:
                component_html += f"""
                    <li>{component_type.name}</li>
                """
            service.total_component_info = component_html

    def _compute_total_component_count(self):
        for service in self:
            service.total_component_count = len(service.component_ids)

    @api.depends("component_ids.price_subtotal")
    def _compute_service_total_price(self):
        for service in self:
            service.total_price = sum(service.component_ids.mapped("price_subtotal"))
