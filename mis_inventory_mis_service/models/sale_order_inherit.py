from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    source_location_id = fields.Many2one(
        "stock.location",
        string="Source Location",
        readonly=True,
        related="picking_ids.location_id",
    )

    def _prepare_delivery_order(
        self, is_reseller=False, picking=None, device=None, order=None
    ):
        StockRule = self.env["stock.rule"]
        StockPicking = self.env["stock.picking"]

        destination_location = self.env.ref("stock.stock_location_customers")
        picking_type_out = self.env.ref("stock.picking_type_out")
        warehouse = self.env.ref("stock.warehouse0")

        if is_reseller:
            source_location = picking.reseller_id.related_location_id
            origin = picking.origin
            partner = picking.partner_id

            sale_line = picking.move_ids.filtered(
                lambda m: m.product_id == device.product_id
            ).sale_line_id

            product_list = [
                {
                    "product": device.product_id,
                    "qty": 1,
                    "uom": device.product_id.uom_id,
                    "sale_line": sale_line,
                    "description": device.product_id.display_name,
                    "reference": picking.name,
                }
            ]
        else:
            source_location = self.env.ref("stock.stock_location_stock")
            origin = order.name
            partner = order.partner_id

            product_list = []

            for line in order.order_line:
                services = line.product_id.service_id

                for product in services.product_ids.filtered(
                    lambda p: p.detailed_type == "product"
                ).product_product_id:
                    product_list.append(
                        {
                            "product": product,
                            "qty": line.product_uom_qty,
                            "uom": line.product_uom,
                            "sale_line": line,
                            "description": line.name,
                            "reference": False,
                        }
                    )

        rule = StockRule.search(
            [
                ("location_src_id", "=", source_location.id),
                ("location_dest_id", "=", destination_location.id),
                ("warehouse_id", "=", warehouse.id),
            ],
            limit=1,
        )

        move_vals = []

        for vals in product_list:
            move_vals.append(
                (
                    0,
                    0,
                    {
                        "name": vals["description"],
                        "origin": origin,
                        "product_id": vals["product"].id,
                        "product_uom_qty": vals["qty"],
                        "product_uom": vals["uom"].id,
                        "location_id": source_location.id,
                        "location_dest_id": destination_location.id,
                        "warehouse_id": warehouse.id,
                        "sale_line_id": vals["sale_line"].id,
                        "rule_id": rule.id if rule else False,
                        "description_picking": vals["description"],
                        "reference": vals["reference"],
                    },
                )
            )

        if not move_vals:
            return False

        delivery_order = StockPicking.create(
            {
                "origin": origin,
                "partner_id": partner.id if not is_reseller else False,
                "picking_type_id": picking_type_out.id,
                "location_id": source_location.id,
                "location_dest_id": destination_location.id,
                "move_ids": move_vals,
            }
        )

        if is_reseller:
            delivery_order.write(
                {
                    "device_imei_ids": [(4, device.id)],
                }
            )

        delivery_order.action_confirm()

        if is_reseller:
            delivery_order.action_assign()

        return delivery_order

    def _create_delivery_order(self):
        for order in self:
            delivery_order = self._prepare_delivery_order(
                is_reseller=False,
                order=order,
            )
            if delivery_order:
                order.picking_ids += delivery_order

    def action_confirm(self):
        """
        Overrides the action_confirm method to create a product sales order
        from service when service sales order is confirmed.
        """
        res = super().action_confirm()
        self._create_delivery_order()
        return res

    def action_cancel(self):
        """
        Overrides the action_cancel method to cancel the linked product
        sales order when the original service sales order is canceled.
        """
        res = super().action_cancel()
        return res