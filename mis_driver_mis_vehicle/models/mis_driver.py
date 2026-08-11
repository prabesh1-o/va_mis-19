from odoo import fields, models


class MisDriver(models.Model):
    _inherit = "mis.driver"

    vehicle_ids = fields.One2many("mis.vehicle", "driver_id", string="Vehicle")
    assigned_vehicle = fields.Char(
        compute="_compute_assigned_vehicles", string="Assigned Vehicle"
    )
    vehicle_history_id = fields.One2many(
        "mis.driver.history", "driver_id", string="Driver History"
    )
    vehicle_history_count = fields.Integer(
        string="Vehicle History", compute="_compute_vehicle_history_count"
    )
    is_vehicle_assigned = fields.Boolean(default=False)

    def _compute_assigned_vehicles(self):
        for driver in self:
            vehicle_numbers = [vehicle.vehicle_number for vehicle in driver.vehicle_ids]
            driver.assigned_vehicle = (
                ", ".join(vehicle_numbers) if vehicle_numbers else ""
            )

    def _compute_vehicle_history_count(self):
        """Compute counts shown in the button box"""
        for driver in self:
            driver.vehicle_history_count = len(driver.vehicle_history_id)
