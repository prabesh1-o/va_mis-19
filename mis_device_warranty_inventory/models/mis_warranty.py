from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisDeviceWarranty(models.Model):
    _inherit = "mis.warranty"

    new_stock_device_id = fields.Many2one(
        "mis.inventory.device", string="New Device IMEI",
    )
    stock_device_id = fields.Many2one(
        "mis.inventory.device", string="Stock Device", compute="_compute_stock_device",
    )
    stock_sim_id = fields.Many2one("mis.inventory.sim",)
    picking_ids = fields.One2many("stock.picking", "mis_warranty_id")
    delivery_count = fields.Integer(
        string="Delivery Orders", compute="_compute_picking_ids"
    )

    @api.onchange("device_id")
    def _compute_stock_device(self):
        """
        Updates the `stock_device_id` field based on the selected `device_id`.
        """
        for warranty in self:
            warranty.stock_device_id = None
            if warranty.device_id:
                stock_device = (
                    self.env["mis.inventory.device"]
                    .with_context(active_test=False)
                    .search([("device_id", "=", warranty.device_id.id)])
                )
                warranty.stock_device_id = stock_device.id

    @api.depends("picking_ids")
    def _compute_picking_ids(self):
        """
        Display total picking count as delivery button in warranty
        """
        for order in self:
            order.delivery_count = len(order.picking_ids)

    def btn_create_installation_order(self):
        """
        Validates whether return delivery is completed or not
        during installation order creation
        """
        self.ensure_one()
        if self.resolution == "replaced":
            return_pickings = self.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "incoming" and p.state in "done"
            )
            if not return_pickings:
                raise UserError(
                    _(
                        "Return Delivery must be created and validated "
                        "from delivery before creating installation order"
                    )
                )
        return super().btn_create_installation_order()

    def _prepare_installation_lines_warranty(self):
        res = super()._prepare_installation_lines_warranty()
        res.update(
            {
                "stock_device_id": (
                    self.new_stock_device_id.id
                    if self.new_stock_device_id
                    else self.stock_device_id.id
                ),
            }
        )
        if self.resolution == "replaced":
            self.action_return_device()
        return res

    def action_return_device(self):
        for order in self:
            is_return = self.env.context.get("is_return", False)
            vendor_location = self.env.ref("stock.stock_location_suppliers")
            customer_location = self.env.ref("stock.stock_location_customers")
            wh_main_location = self.env.ref("stock.stock_location_stock")

            warehouse = self.env.ref("stock.warehouse0")
            company = self.env.ref("base.main_company")

            if is_return:
                picking_type_id = self.env["stock.picking.type"].search(
                    [("code", "=", "incoming"), ("name", "=", "Returns")]
                )
                source_location = vendor_location
                destination_location = wh_main_location
            else:
                picking_type_id = self.env.ref("stock.picking_type_out")
                source_location = wh_main_location
                destination_location = customer_location
            move_ids = [
                (
                    0,
                    0,
                    {
                        "name": order.device_id.product_id.name,
                        "company_id": company.id,
                        "product_id": order.device_id.product_id.product_product_id.id,
                        "warehouse_id": warehouse.id,
                        "location_id": source_location.id,
                        "location_dest_id": destination_location.id,
                        "partner_id": order.customer_id.id,
                        "picking_type_id": picking_type_id.id,
                    },
                )
            ]
            if move_ids:
                return_order = self.env["stock.picking"].create(
                    {
                        "partner_id": order.customer_id.id,
                        "location_id": source_location.id,
                        "location_dest_id": destination_location.id,
                        "picking_type_id": picking_type_id.id,
                        "scheduled_date": order.received_date,
                        "move_ids": move_ids,
                    }
                )
        order.picking_ids += return_order

    def action_view_delivery(self):
        self.ensure_one()
        picking_ids = self.picking_ids
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        action["context"] = {"search_default_mis_warranty_id": picking_ids}
        if len(picking_ids) == 1:
            action["view_mode"] = "form"
            action["res_id"] = picking_ids[0].id
            if "views" in action:
                action["views"] = [
                    (view_id, view_type)
                    for view_id, view_type in action["views"]
                    if view_type == "form"
                ]
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", picking_ids.ids)]
        return action
