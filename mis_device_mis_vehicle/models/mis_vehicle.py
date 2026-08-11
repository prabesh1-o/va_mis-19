from odoo import fields, models


class MisVehicle(models.Model):
    _inherit = "mis.vehicle"

    device_ids = fields.One2many("mis.device", "vehicle_id", string="IMEI no.")
    customer_id = fields.Many2one(
        "res.partner", compute="_compute_customer_ids", string="Customer"
    )

    def _compute_customer_ids(self):
        for vehicle in self:
            if vehicle.device_ids:
                customer_id = vehicle.device_ids.customer_id.ids
                vehicle.customer_id = (
                    customer_id[0] if customer_id else None
                )  # some devices have many customers
            else:
                vehicle.customer_id = None
