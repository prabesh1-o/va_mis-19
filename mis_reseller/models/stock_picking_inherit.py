from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reseller_id = fields.Many2one("mis.reseller", string="Reseller")

    def button_validate(self):
        self._check_internal_product_availability()
        res = super().button_validate()
        if self.picking_type_code == "internal" and self.reseller_id:

            for device in self.device_imei_ids:
                device.reseller_id = self.reseller_id
            self.update_qty_sale_order()
        return res

    def update_qty_sale_order(self):
        if self.is_received and self.picking_type_code == "internal":
            for move in self.move_ids.filtered(lambda m: m.sale_line_id):
                sale_line = move.sale_line_id
                sale_line.qty_delivered = sale_line.product_uom_qty

    def action_received_return(self):
        res = super().action_received_return()
        for picking in self:
            if (
                picking.is_received
                and picking.reseller_id
                and picking.picking_type_code == "internal"
            ):
                device_imeis = picking.device_imei_ids
                for device in device_imeis:
                    delivery_order = self.env["sale.order"]._prepare_delivery_order(
                        is_reseller=True, picking=picking, device=device
                    )
                    delivery_order.action_confirm()
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    reseller_id = fields.Many2one("mis.reseller")
