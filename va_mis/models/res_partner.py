from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Customer"
    _rec_names_search = ["name", "username", "ref", "vat", "company_registry"]

    username = fields.Char(string="Username")
    is_billed_customer = fields.Boolean(string="Billed Customer", default=False)
    is_customer = fields.Boolean(string="Customer", default=False)
    agreement = fields.Binary(string="Agreement")

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner in partners:
            if partner.parent_id:
                partner.is_customer = False
        return partners
