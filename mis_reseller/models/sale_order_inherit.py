from odoo import fields, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reseller_id = fields.Many2one("mis.reseller", string="Reseller")
    is_reseller_order = fields.Boolean(
            string="Reseller Order",
            default=False,
            index=True,
        )
    

    def _create_delivery_order(self):
        super()._create_delivery_order()
        for order in self:
            if order.reseller_id and order.picking_ids:
                destination_location = self.reseller_id.related_location_id
                internal_picking = self.env.ref("stock.picking_type_internal")
                sequence = internal_picking.sequence_id
                for picking in order.picking_ids:
                    picking.write(
                        {
                            "name": sequence.next_by_id(),
                            "location_dest_id": destination_location.id,
                            "picking_type_id": internal_picking.id,
                            "reseller_id": order.reseller_id.id,
                        }
                    )
                    picking.move_ids.write(
                        {
                            "location_dest_id": destination_location.id,
                            "reseller_id": order.reseller_id.id,
                        }
                    )

    def _get_action_view_picking(self, pickings):
        action = super()._get_action_view_picking(pickings)

        if self.reseller_id:
            extra_domain = [("picking_type_code", "!=", "outgoing")]
            if "domain" in action:
                action["domain"] = expression.AND([action["domain"], extra_domain])
            else:
                action["domain"] = extra_domain

        return action

    def _compute_picking_ids(self):
        super()._compute_picking_ids()
        for order in self:
            if order.reseller_id:
                delivery_count = len(
                    order.picking_ids.filtered(
                        lambda p: p.picking_type_code == "internal"
                    )
                )
                order.delivery_count = delivery_count

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.reseller_id:
            res["reseller_id"] = self.reseller_id.id
        return res


class AccountMove(models.Model):
    _inherit = "account.move"

    reseller_id = fields.Many2one("mis.reseller", string="Reseller")
