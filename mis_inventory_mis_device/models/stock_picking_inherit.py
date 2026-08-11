from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    device_imei_ids = fields.Many2many(
        "mis.inventory.device",
        string="Device IMEI",
        required=True,
        context={"active_test": False},
    )

    def action_received_return(self):
        self._check_internal_product_availability()
        for picking in self:
            if picking.picking_type_code == "internal" and not picking.device_imei_ids:
                raise ValidationError(_("Please add the devices to transfer"))
            for move in picking.move_ids:
                self._validate_product_availability(move)
            order_lines = picking.move_ids.mapped("sale_line_id")
            if order_lines:
                order_qty = sum(order_lines.mapped("product_uom_qty"))
                if len(self.device_imei_ids) != order_qty:
                    raise ValidationError(
                        _(
                            "The number of devices does not match the number of order lines."
                        )
                    )

            for device in picking.device_imei_ids:
                device.location_id = picking.location_dest_id
        return super().action_received_return()

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
