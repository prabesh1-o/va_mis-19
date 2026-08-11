from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LeadRawData(models.Model):
    _inherit = "lead.raw.data"

    required_service_ids = fields.Many2many(
        "mis.services.menu", string="Required Service"
    )
    raw_lead_service_line_ids = fields.One2many(
        "lead.raw.data.service.line", "raw_lead_id", "Services", tracking=True
    )

    @api.depends("raw_lead_service_line_ids.amount")
    def _compute_total_amount(self):
        for lead in self:
            lead.total_amount = sum(lead.raw_lead_service_line_ids.mapped("amount"))


class LeadRawDataServiceLine(models.Model):
    _name = "lead.raw.data.service.line"
    _description = "Lead Raw Data Service Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    raw_lead_id = fields.Many2one("lead.raw.data")
    company_currency_id = fields.Many2one(related="raw_lead_id.company_currency_id")
    service_price = fields.Monetary(
        compute="_compute_service_price",
        currency_field="company_currency_id",
        string="Actual Price",
        store=True,
    )
    discount_percentage = fields.Float(string="Discount(%)")
    final_price = fields.Monetary(
        compute="_compute_final_price",
        currency_field="company_currency_id",
        string="Price",
        store=True,
    )
    offered_price = fields.Monetary(
        currency_field="company_currency_id", string="Offered Price"
    )
    quantity = fields.Integer(string="Quantity")
    amount = fields.Monetary(
        compute="_compute_amount",
        currency_field="company_currency_id",
        string="Amount",
        store=True,
    )
    service_id = fields.Many2one(
        "mis.services", string="Service", domain="[('id', 'in', service_domain_ids)]"
    )
    service_domain_ids = fields.Many2many(
        "mis.services", compute="_compute_service_domain_ids"
    )
    renewal_price = fields.Monetary(
        currency_field="company_currency_id", string="Renewal Price"
    )

    @api.depends("raw_lead_id.required_service_ids")
    def _compute_service_domain_ids(self):
        for line in self:
            if line.raw_lead_id.required_service_ids:
                line.service_domain_ids = (
                    line.raw_lead_id.required_service_ids.service_ids.ids
                )
            else:
                line.service_domain_ids = self.env["mis.services"].search([]).ids

    @api.depends("service_id")
    def _compute_service_price(self):
        for line in self:
            if line.service_id:
                line.service_price = line.service_id.total_price

    @api.depends("quantity", "final_price")
    def _compute_amount(self):
        for line in self:
            if line.final_price and line.quantity:
                line.amount = line.final_price * line.quantity
            else:
                line.amount = 0

    @api.depends("discount_percentage", "service_price")
    def _compute_final_price(self):
        for service_line in self:
            discount_percent = service_line.discount_percentage
            if discount_percent and service_line.service_price:
                if 0 < discount_percent <= 100:
                    service_line.final_price = (
                        service_line.service_price
                        - (discount_percent / 100) * service_line.service_price
                    )
                else:
                    raise UserError(
                        _("Discount percentage cannot be less than 0 or more than 100.")
                    )
            else:
                service_line.final_price = service_line.service_price
