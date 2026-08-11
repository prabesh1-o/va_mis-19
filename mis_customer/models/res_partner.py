from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    reference_id = fields.Char(
        string="Reference ID", compute="_compute_customer_id", store=True
    )
    industry_id = fields.Many2one("mis.customer.industry")

    @api.depends("industry_id")
    def _compute_customer_id(self):
        """
        Computes and assigns a unique reference ID based on the partner's
        creation date, industry prefix, and ID, if not already set.
        """
        for partner in self:
            if not partner.reference_id and partner.id and partner.industry_id:
                partner.reference_id = self._get_reference_id(
                    partner.create_date, partner.industry_id.prefix, partner.id
                )

    def _get_reference_id(self, create_date, industry_prefix, id):
        """
        Generates a reference ID using the creation date, industry prefix,
        and partner's ID, formatted as 'prefix-year-0000'.
        """
        create_year = (fields.Datetime.from_string(create_date)).year
        reference_id = f"{industry_prefix}-{create_year}-{str(id).zfill(4)}"
        return reference_id

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the create method to generate and assign a unique reference ID
        to each partner upon creation, based on their industry.
        """
        partners = super().create(vals_list)
        for partner in partners:
            if partner.industry_id:
                partner.reference_id = self._get_reference_id(
                    partner.create_date, partner.industry_id.prefix, partner.id
                )
        return partners
