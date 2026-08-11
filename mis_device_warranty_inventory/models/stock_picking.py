from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    mis_warranty_id = fields.Many2one("mis.warranty")

    def button_validate(self):
        res = super().button_validate()
        if self.mis_warranty_id:
            if self.picking_type_code == "incoming":
                self._return_devices_and_sim()
        return res

    def _return_devices_and_sim(self):
        device_imei = self.mis_warranty_id.device_id

        inventory_imei = self.device_imei_ids.search(
            [("imei_no", "=", device_imei.imei_no), ("active", "=", False)]
        )
        inventory_sim = self.env["mis.inventory.sim"].search(
            [("sim_no", "=", device_imei.sim.sim_no), ("active", "=", False)]
        )
        if inventory_imei and inventory_sim:
            inventory_imei.active = True
            inventory_sim.active = True
        if device_imei.state == "active":
            device_imei.state = "inactive"
