import json

from lxml import etree
from odoo import api, fields, models
from odoo.osv.expression import OR


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_default_fiscal_period(self):
        """
        Returns the ID of the active fiscal period, or None if not found.
        """
        return (
            self.env["mis.fiscal.period"].search([("is_active", "=", True)]).id or None
        )

    poc_name = fields.Char(string="POC Name")
    poc_phone = fields.Char(string="POC Phone")
    required_service_ids = fields.Many2many(
        "mis.services.menu", string="Required Service"
    )
    invoice_status = fields.Selection(
        selection_add=[("partially_invoiced", "Partially Invoiced"),],
    )
    discount = fields.Float(string="Disc(%)", default=0.0)
    discount_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_discount_amount", store=True,
    )
    amount_residual = fields.Monetary(
        string="Amount Due",
        compute="_compute_amount_residual",
        group_operator="sum",
        store=True,
    )
    product_uom_qty = fields.Float(
        string="Quantity", compute="_compute_quantity", store=True
    )
    qty_delivered = fields.Float(
        string="Delivered", compute="_compute_quantity", store=True
    )
    qty_invoiced = fields.Float(
        string="Invoiced", compute="_compute_quantity", store=True
    )
    amount_invoiced = fields.Monetary(
        string="Invoiced Amt.",
        compute="_compute_amount_invoiced",
        group_operator="sum",
        store=True,
    )
    note_id = fields.Many2one(
        "mis.note.template",
        string="Template",
        help="This is the template for terms & conditions.",
    )
    fiscal_period_id = fields.Many2one(
        "mis.fiscal.period", string="Fiscal Year", default=_get_default_fiscal_period,
    )

    @api.depends(
        "order_line.invoice_lines.move_id.payment_state",
        "order_line.invoice_lines.move_id.amount_total",
        "order_line.invoice_lines.move_id.amount_residual",
        "state",
    )
    def _compute_amount_residual(self):
        for order in self:
            total_paid = 0
            for invoice in order.invoice_ids.filtered(lambda i: i.state != "cancel"):
                total_paid += invoice.amount_total - invoice.amount_residual
            order.amount_residual = order.amount_total - total_paid

    def _compute_invoice_status(self):
        super()._compute_invoice_status()
        for order in self:
            if any(
                s == "partially_invoiced"
                for s in order.order_line.mapped("invoice_status")
            ):
                order.invoice_status = "partially_invoiced"

    @api.onchange("discount")
    @api.depends("discount")
    def _compute_discount(self):
        """
        Apply the specified discount to the order lines
        based on the discount directly.
        """
        for order in self:
            for line in order.order_line:
                line.discount = order.discount

    @api.depends("order_line.discount_amount")
    def _compute_discount_amount(self):
        """
        Calculate the total discount amount for the order by summing
        the discount amounts from all order lines.
        """
        for order in self:
            order.discount_amount = sum(
                line.discount_amount for line in order.order_line
            )

    @api.depends("note_id")
    def _compute_note(self):
        res = super()._compute_note()
        for order in self:
            if order.note_id:
                order.note = order.note_id.note
        return res

    @api.depends("order_line.qty_invoiced", "invoice_ids.amount_total")
    def _compute_amount_invoiced(self):
        """
        Calculate the total invoiced amount for the order by summing
        the total amounts from all invoices.
        """
        for order in self:
            order.amount_invoiced = sum(
                invoice.amount_total for invoice in order.invoice_ids
            )

    @api.depends(
        "order_line.qty_invoiced",
        "order_line.product_uom_qty",
        "order_line.qty_delivered",
        "order_line.product_template_id.service_id",
    )
    def _compute_quantity(self):
        """
        Calculate the quantities of product with service
        by summing the quantities from all order lines.
        """
        for order in self:
            total_product_uom_qty = 0
            total_qty_delivered = 0
            total_qty_invoiced = 0
            for line in order.order_line:
                if line.product_template_id.service_id:
                    total_product_uom_qty += line.product_uom_qty
                    total_qty_delivered += line.qty_delivered
                    total_qty_invoiced += line.qty_invoiced
            order.product_uom_qty = total_product_uom_qty
            order.qty_delivered = total_qty_delivered
            order.qty_invoiced = total_qty_invoiced

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        This method extends the standard get_view functionality by adding automatic readonly
        behavior to form fields(except tag_ids and user_id) based on the record's state.
        When a record's state is not 'draft' or 'sent', all editable fields will become readonly,
        implementing a common workflow pattern where records can only be
        modified in draft or sent state.

        Args:
            view_id (int, optional): The ID of the view to load. Defaults to None,
                which loads the default view of the specified type.
            view_type (str, optional): The type of view to load. Defaults to "form".
                Only form views are modified by this override.
            **options: Additional options passed to the original get_view method.

        Returns:
            dict: View definition dictionary containing:
                - 'arch': The view's XML architecture as a string
                - Other view-related data from the original get_view
        """
        res = super().get_view(view_id=view_id, view_type=view_type, **options,)
        if view_type == "form":
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name][not(ancestor::field)]"):
                field_name = field.attrib.get("name")
                if field_name in ["tag_ids", "user_id"]:
                    continue
                modifiers = json.loads(
                    field.attrib.get("modifiers", '{"readonly": false}')
                )
                if modifiers.get("readonly") is not True:
                    modifiers["readonly"] = OR(
                        [
                            modifiers.get("readonly", []) or [],
                            [("state", "not in", ["draft", "sent"])],
                        ]
                    )
                    field.attrib["modifiers"] = json.dumps(modifiers)
            res["arch"] = etree.tostring(doc, pretty_print=True)
        return res
