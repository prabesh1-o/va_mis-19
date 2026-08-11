from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_installation_order(self):
        super().action_create_installation_order()
        return self.picking_ids.action_confirm()

    def _prepare_installation_lines(self, line):
        res = super()._prepare_installation_lines(line)
        res.update(
            {
                "sale_order_line_id": line.id,
                "stock_move_ids": [(4, move.id) for move in line.move_ids],
            }
        )
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_code == "outgoing":
                sale_order = picking.sale_id
                if sale_order:
                    order_lines = sale_order.order_line.filtered(
                        lambda line: any(
                            move.picking_id == picking for move in line.move_ids
                        )
                    )
                    self._change_qty_delivered(order_lines)
        return res

    def _change_qty_delivered(self, order_lines):
        for order_line in order_lines:
            if order_line.installation_line_ids:
                installed_service = len(
                    order_line.installation_line_ids.filtered(
                        lambda x: x.state == "installed"
                    )
                )
                canceled_service = len(
                    order_line.installation_line_ids.filtered(
                        lambda x: x.state == "canceled"
                    )
                )
                order_line.qty_delivered = installed_service
                order_line.qty_cancelled = canceled_service
            else:
                if self.partner_id.is_customer:
                    qty = sum(order_line.move_ids.mapped("reserved_availability"))
                    order_line.qty_delivered += qty
