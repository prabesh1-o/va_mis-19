from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisBulkPayments(models.Model):
    _name = "mis.bulk.payment"
    _description = "mis bulk payment"
    _rec_name = "customers"

    customers = fields.Many2one(
        "res.partner", string="Customers", domain="[('is_customer', '=', True)]"
    )
    customer_invoice_ids = fields.One2many(
        "account.move",
        "bulk_payment_id",
        string="Customer Invoices",
        compute="_compute_customer_invoices",
        readonly=False,
    )
    outbound_payment_ids = fields.One2many(
        "account.payment",
        "bulk_payment_id",
        string="Customer Credits",
        compute="_compute_outbound_payments",
        readonly=False,
        order="date desc",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.onchange("customers")
    def _compute_customer_invoices(self):
        self.ensure_one()
        for record in self:
            if record.customers:
                record.customer_invoice_ids = self.env["account.move"].search(
                    [
                        ("partner_id", "=", record.customers.id),
                        ("move_type", "in", ["out_invoice"]),
                        ("state", "in", ["posted"]),
                        ("payment_state", "in", ["not_paid", "partial"]),
                    ],
                    order="invoice_date asc",
                )
            else:
                record.customer_invoice_ids = self.env["account.move"]

    @api.onchange("customers")
    def _compute_outbound_payments(self):
        self.ensure_one()
        for record in self:
            if record.customers:
                record.outbound_payment_ids = self.env["account.payment"].search(
                    [
                        ("partner_id", "=", record.customers.id),
                        ("is_reconciled", "!=", True),
                        ("state", "in", ["posted", "draft"]),
                    ]
                )
            else:
                record.outbound_payment_ids = self.env["account.payment"]

    def action_open_payment(self):
        self.ensure_one()
        if not self.customers:
            raise UserError(_("Please select a customer first."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Register Payment"),
            "res_model": "account.payment",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.customers.id,
                "default_partner_type": "customer",
                "default_payment_type": "inbound",
                "default_currency_id": self.currency_id.id,
                "default_date": fields.Date.today(),
                "default_journal_id": self.env["account.journal"]
                .search([("type", "=", "bank")], limit=1)
                .id,
            },
        }

    def action_pay(self):
        self.ensure_one()

        if not self.customer_invoice_ids or not self.outbound_payment_ids:
            raise UserError(_("No invoices or customer credits available to process"))

        posted_payments = self.outbound_payment_ids.filtered(
            lambda p: p.state == "posted"
        )

        if posted_payments:
            sorted_invoices = self._get_sorted_invoices()
            sorted_credits = self._get_sorted_credits()
            for credit in sorted_credits:
                available_credit = credit.amount
                credit_lines = self._get_credit_lines(credit)

                for invoice in sorted_invoices:
                    if available_credit <= 0:
                        break

                    invoice_lines = self._get_invoice_lines(invoice)

                    if not invoice_lines:
                        continue

                    available_credit = self._apply_credit_to_invoice(
                        invoice, invoice_lines, credit_lines, available_credit
                    )
        return True

    def _get_sorted_invoices(self):
        return sorted(self.customer_invoice_ids, key=lambda inv: inv.sequence)

    def _get_sorted_credits(self):
        """
        Get unreconciled lines from a credit.
        """
        return sorted(
            self.outbound_payment_ids.filtered(lambda cr: cr.state == "posted"),
            key=lambda cr: cr.sequence,
        )

    def _get_credit_lines(self, credit):
        return credit.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
            and not l.reconciled
        )

    def _get_invoice_lines(self, invoice):
        """
        Get unreconciled lines from an invoice.
        """
        return invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == "asset_receivable"
            and not l.reconciled
        )

    def _apply_credit_to_invoice(
        self, invoice, invoice_lines, credit_lines, available_credit
    ):
        """
        Apply credit to an invoice and return the remaining available credit.
        """
        invoice_amount = invoice.amount_residual
        reconcile_amount = min(available_credit, invoice_amount)
        if reconcile_amount > 0:
            lines_to_reconcile = (invoice_lines + credit_lines).filtered(
                lambda l: not l.reconciled
            )
            lines_to_reconcile.with_context(amount=reconcile_amount).reconcile()
            available_credit -= reconcile_amount
            invoice.invalidate_cache(["amount_residual", "payment_state"])

        return available_credit


class AccountMove(models.Model):
    _inherit = "account.move"

    sequence = fields.Integer(string="Sequence")
    bulk_payment_id = fields.Many2one("mis.bulk.payment", string="Bulk Payment")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sequence = fields.Integer(string="Sequence")
    bulk_payment_id = fields.Many2one("mis.bulk.payment", string="Bulk Payment")
    remaining_credit = fields.Monetary(
        string="Remaining Credit", compute="_compute_remaining_credit", store=True,
    )

    @api.depends("amount_company_currency_signed", "reconciled_invoice_ids")
    def _compute_remaining_credit(self):
        for payment in self:
            applied_amount = sum(payment.reconciled_invoice_ids.mapped("amount_total"))
            payment.remaining_credit = (
                payment.amount_company_currency_signed - applied_amount
            )
