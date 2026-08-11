from datetime import timedelta

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_default_fiscal_period(self):
        """
        Returns the ID of the active fiscal period, or None if not found.
        """
        return (
            self.env["mis.fiscal.period"].search([("is_active", "=", True)]).id or None
        )

    npa = fields.Boolean(string="NPA", default=False, tracking=True)
    npa_date = fields.Date(string="NPA date", compute="_compute_npa_date",store=True)
    note_id = fields.Many2one(
        "mis.note.template",
        string="Template",
        help="This is the template for terms & conditions.",
    )
    tag_ids = fields.Many2many("account.move.tag", string="Tags")
    fiscal_period_id = fields.Many2one(
        "mis.fiscal.period", string="Fiscal Year", default=_get_default_fiscal_period,
    )

    @api.depends("invoice_date_due", "payment_state")
    def _compute_npa_date(self):
        days_count = int(
            self.env["ir.config_parameter"].sudo().get_param("mis.npa_days_count")
        )
        for invoice in self:
            if invoice.invoice_date_due and invoice.payment_state != "paid":
                invoice.npa_date = invoice.invoice_date_due + timedelta(days=days_count)
            else:
                invoice.npa_date = None

    @api.depends("note_id")
    def _compute_narration(self):
        res = super()._compute_narration()
        for invoice in self:
            if invoice.note_id:
                invoice.narration = invoice.note_id.note
        return res


class AccountMoveTags(models.Model):
    _name = "account.move.tag"
    _description = "Acount Move Tags"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color", default=0)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        invoices = self.env["account.move"].browse(self._context.get("active_ids", []))
        for invoice in invoices:
            if invoice.payment_state == "paid":
                invoice.npa = False
        return res
