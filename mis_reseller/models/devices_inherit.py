from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisInventoryDevice(models.Model):
    _inherit = "mis.inventory.device"

    reseller_id = fields.Many2one("mis.reseller", string="Reseller")
    delivery_count = fields.Integer(
        string="Delivery Count", compute="_compute_delivery_count"
    )
    stock_sim_id = fields.Many2one("mis.inventory.sim", string="Sim")
    is_device_created = fields.Boolean(string="Is Device Created", default=False)

    def _verify_device_out_delivery(self):
        pending_delivery = self.env["stock.picking"].search(
            [
                ("device_imei_ids", "in", self.id),
                ("picking_type_id.code", "=", "outgoing"),
            ]
        )
        if pending_delivery.state != "done":
            raise ValidationError(
                _("Please verify the delivery before creating a device.")
            )

    def action_register_devices(self):
        self.ensure_one()
        if not self.stock_sim_id:
            raise ValidationError(_("Please select a sim number."))
        self._verify_device_out_delivery()
        stock_sim = self.stock_sim_id
        sim_record = self.env["mis.device.sim"].create(
            {
                "sim_no": stock_sim.sim_no,
                "sim_carrier": stock_sim.sim_carrier,
                "data_plan": stock_sim.data_plan,
                "serial_no": stock_sim.serial_no,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Mis Device",
            "res_model": "mis.device",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_imei_no": self.imei_no,
                "default_device_model_id": self.device_model_id.id,
                "default_product_id": self.product_id.mis_product_id.id or False,
                "default_reseller_id": self.reseller_id.id,
                "default_sim": sim_record.id,
            },
        }

    def action_view_out_delivery(self):
        self.ensure_one()
        delivery_orders = self.env["stock.picking"].search(
            [
                ("device_imei_ids", "=", self.id),
                ("picking_type_id.code", "=", "outgoing"),
            ]
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Delivery Orders",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", delivery_orders.ids)],
            "context": {"default_device_imei_ids": [self.id]},
        }

    def _compute_delivery_count(self):
        for record in self:
            delivery_orders = self.env["stock.picking"].search(
                [
                    ("device_imei_ids", "=", self.id),
                    ("picking_type_id.code", "=", "outgoing"),
                ]
            )
            record.delivery_count = len(delivery_orders)


class MisDevice(models.Model):
    _inherit = "mis.device"

    reseller_id = fields.Many2one("mis.reseller", string="Reseller")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if record.imei_no and record.sim.sim_no:
                inventory_device = self.env["mis.inventory.device"].search(
                    [("imei_no", "=", record.imei_no), ("active", "=", True)], limit=1
                )
                if inventory_device:
                    inventory_sim = inventory_device.stock_sim_id.search(
                        [("sim_no", "=", record.sim.sim_no), ("active", "=", True)]
                    )
                inventory_device.active = False
                inventory_sim.active = False
                inventory_device.is_device_created = True
        return res
