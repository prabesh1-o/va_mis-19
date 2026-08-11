from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    delivery_count = fields.Integer(
        string="Delivery Orders", compute="_compute_picking_ids"
    )

    source_location_id = fields.Many2one(
        "stock.location",
        string="Source Location",
        readonly=False,
        related="sale_order_id.picking_ids.location_id",
        domain=[("usage", "=", "internal")],
    )

    @api.onchange("source_location_id")
    def _onchange_move_location_id(self):
        pickings = self.sale_order_id.picking_ids.filtered(
            lambda s: s.state not in ["done", "cancel"]
        )
        for picking in pickings:
            for line in picking.move_line_ids:
                line.location_id = self.source_location_id

    def action_view_delivery(self):
        if self.sale_order_id:
            pickings = self.sale_order_id.picking_ids
            if pickings:
                return self.env["sale.order"]._get_action_view_picking(pickings)

    @api.depends("sale_order_id.picking_ids")
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.sale_order_id.picking_ids)

    def btn_configure_customer_and_devices(self):
        super().btn_configure_customer_and_devices()
        for line in self:
            for sale_order in line.sale_order_id:
                for picking in sale_order.picking_ids.filtered(
                    lambda s: s.state != "cancel"
                ):
                    if not self._is_picking_validated(picking):
                        raise ValidationError(
                            _("Please validate the Delivery from Inventory")
                        )

    def _is_picking_validated(self, picking):
        if picking.backorder_id:
            for backorder in picking.backorder_id:
                if not self._is_picking_validated(backorder):
                    return False
        elif picking.state != "done":
            return False
        return True


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    stock_move_ids = fields.Many2many(
        "stock.move", "mis_device_installation_line_stock_move_rel"
    )

    def btn_update_installation_state(self):
        super().btn_update_installation_state()
        for line in self:
            for sol in line.sale_order_line_id:
                valid_moves = sol.move_ids.filtered(
                    lambda move: move.state not in ["done", "cancel"]
                    and self._check_delivery_state(move)
                )
                if valid_moves:
                    for move in valid_moves:
                        if not move.product_id.detailed_type == "consu":
                            self._validate_product_availability(move)
                        self._update_quantity_done(move)

    def _check_delivery_state(self, move):
        """Check if the associated picking is in a valid state for processing."""
        return move.picking_id.state not in ["draft", "done", "cancel"]

    def _validate_product_availability(self, move):
        prod_quant = (
            self.env["stock.quant"]
            .search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_id", "=", move.location_id.id),
                ]
            )
            .available_quantity
        )
        if prod_quant <= 0:
            raise ValidationError(
                _(
                    f"Product {move.product_id.name} not available in {move.location_id.complete_name}"
                )
            )
        else:
            return True

    def _update_quantity_done(self, move):
        product_type = move.product_id
        product_quantity = (
            product_type.mis_product_id.quantity
            if product_type.mis_product_id
            else min(product_type.service_id.product_ids.mapped("quantity"))
        )
        if self.state == "installed":
            move.quantity_done += product_quantity
        if self.state != "installed":
            move.quantity_done -= product_quantity
