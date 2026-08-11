from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    device_imei_ids = fields.One2many(
        "mis.inventory.device", "product_id", string="IMEI Devices"
    )
    imei_count = fields.Integer(string="IMEI Count", compute="_compute_imei_count")

    @api.depends("device_imei_ids")
    def _compute_imei_count(self):
        for product in self:
            product.imei_count = len(product.device_imei_ids)

    def action_view_imei_devices(self):
        self.ensure_one()
        return {
            "name": "IMEI Devices",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "mis.inventory.device",
            "domain": [("product_id", "=", self.id)],
            "context": {"default_product_id": self.id},
        }
