from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisFiscalPeriod(models.Model):
    _name = "mis.fiscal.period"
    _description = "MIS Fiscal Period"

    name = fields.Char(string="Fiscal Year", required=True)
    is_active = fields.Boolean(string="Active", default=False)
    fiscal_start = fields.Date(string="Start", required=True)
    fiscal_end = fields.Date(string="End", required=True)

    @api.constrains("is_active")
    def _validate_active_fiscal_period(self):
        """
        Ensures only one fiscal period is active at a time; raises error if multiple are active.
        """
        for period in self:
            count = self.env["mis.fiscal.period"].search_count(
                [("is_active", "=", True), ("id", "!=", period.id)]
            )
            if period.is_active and count:
                raise UserError(_("Only one fiscal period can be active at a time!"))
