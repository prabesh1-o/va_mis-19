from odoo import models


class StockQuantLocation(models.Model):
    _inherit = "stock.quant"

    def action_view_devices(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mis_inventory_mis_device.action_mis_inventory_device"
        )
        action["domain"] = [
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", self.location_id.id),
        ]
        action["context"] = {"search_default_group_by_location": False, "create": False}
        return action
