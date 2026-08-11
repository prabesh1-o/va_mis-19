from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisVehicle(models.Model):
    _inherit = "mis.vehicle"

    driver_id = fields.Many2one(
        "mis.driver", string="Driver", domain="[('is_vehicle_assigned','=', False)]"
    )
    driver_history_count = fields.Integer(compute="_compute_driver_history_count")
    driver_history_id = fields.One2many(
        "mis.driver.history", "vehicle_id", string="Driver History"
    )

    def _compute_driver_history_count(self):
        """
        Compute all counts shown in the button box
        """
        for vehicle in self:
            vehicle.driver_history_count = len(vehicle.driver_history_id)

    @api.onchange("driver_id")
    @api.depends("driver_id")
    def validate_driver_change(self):
        """
        doesnot allow to assign driver that has already been assigned
        """
        if any(not rec.end_date for rec in self.driver_history_id):
            raise UserError(
                _(
                    "You cannot change the driver until the end date of the current driver is entered."
                )
            )

    def create_driver_history(self):
        """
        Create driver history of vehicle when driver is changed
        """
        for vehicle in self:
            if vehicle.driver_id:
                vehicle.driver_id.is_vehicle_assigned = True
                create_values = {
                    "driver_id": vehicle.driver_id.id,
                    "start_date": date.today(),
                    "vehicle_id": vehicle.id,
                }
                self.env["mis.driver.history"].create(create_values)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides a create method
        """
        res = super().create(vals_list)
        if res.driver_id:
            res.create_driver_history()
        return res

    def write(self, vals):
        """
        Overrides a create method
        """
        res = super().write(vals)
        if self.driver_id:
            self.create_driver_history()
        return res
