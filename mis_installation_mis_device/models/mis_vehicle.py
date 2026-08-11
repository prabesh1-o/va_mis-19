from odoo import fields, models


class MisVehicle(models.Model):
    _inherit = "mis.vehicle"

    installation_history_ids = fields.One2many(
        "mis.device.installation.history", "vehicle_id", string="Installation History"
    )
    installation_history_count = fields.Integer(
        compute="_compute_device_installation_history_count"
    )

    def _compute_device_installation_history_count(self):
        for vehicle in self:
            vehicle.installation_history_count = len(vehicle.installation_history_ids)
