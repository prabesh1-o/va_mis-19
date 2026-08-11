from odoo import api, fields, models


class MISServiceComponent(models.Model):
    _name = "mis.service.components"
    _description = "MIS Service Components"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    component_type = fields.Many2one(
        "mis.service.components.type", string="Component Type"
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    price = fields.Monetary(
        string="Price", currency_field="company_currency_id", required=True,
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    description = fields.Html()
    price_subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="company_currency_id",
        compute="_compute_price_subtotal",
    )

    @api.depends("price", "quantity")
    def _compute_price_subtotal(self):
        for component in self:
            if component.quantity:
                component.price_subtotal = component.price * component.quantity


class MISServiceComponentType(models.Model):
    _name = "mis.service.components.type"
    _description = "Mis Service Components Type"

    name = fields.Char(string="Name", required=True)
