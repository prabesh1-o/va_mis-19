from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    carrier_name = fields.Char(string="Carrier Name", required=False, tracking=True)
    contact_info = fields.Char(string="Contact Information")
    route = fields.Selection([("air", "Air"), ("road", "Road")], string="Route")
    tracking_number = fields.Char(string="Tracking Number", tracking=True)
    contact_info = fields.Char(string="Contact Information")
    tracking_url = fields.Char(string="Tracking URL")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    shipping_fee = fields.Monetary(
        currency_field="company_currency_id", string="Shipping Fee", tracking=True
    )
    is_received = fields.Boolean(string="Product Received", default=False)
    received_date = fields.Datetime(string="Received Date", tracking=True)
    received_by = fields.Many2one("res.users", string="Received By", readonly=True)

    def action_received_return(self):
        self.is_received, self.received_date, self.received_by = (
            True,
            fields.Datetime.now(),
            self.env.user,
        )

    def button_validate(self):
        res = super().button_validate()
        self._check_internal_product_availability()
        self._is_received_validate()
        self._source_location_in_sales_order()
        return res

    def _check_internal_product_availability(self):
        for picking in self:
            if picking.picking_type_code == "internal" and picking.state not in [
                "cancel",
                "done",
            ]:
                for move in picking.move_ids_without_package:
                    product_qty_available = move.product_id.with_context(
                        location=move.location_id.id
                    ).qty_available
                    if product_qty_available <= 0:
                        raise UserError(
                            _(
                                f"The product {move.product_id.display_name} does not exist "
                                f"in the source location {move.location_id.display_name}."
                            )
                        )

    def _is_received_validate(self):
        if self.picking_type_code == "internal" and not self.is_received:
            raise UserError(
                _(
                    "Transfer can't be validated until products arrive at"
                    " the destination. Please recieve from Shipping Info"
                )
            )

    def _source_location_in_sales_order(self):
        for picking in self:
            if picking.state == "done" and picking.sale_id:
                source_location = picking.location_id
                sale_id = picking.sale_id
                sale_id.source_location_id = source_location

    @api.constrains("carrier_name")
    def _check_carrier_field(self):
        for record in self:
            if record.picking_type_code == "internal" and not record.carrier_name:
                raise ValidationError(
                    _(
                        "Shipping Info incomplete."
                        "Set the Carrier Name and other details from Shipping Info"
                    )
                )

    @api.model
    def create(self, vals):
        picking = super().create(vals)
        picking._check_internal_product_availability()
        return picking

    def write(self, vals):
        res = super().write(vals)
        self._check_internal_product_availability()
        return res
