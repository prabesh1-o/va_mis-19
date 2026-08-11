from odoo import fields, models


class MisDriverHistory(models.Model):
    _name = "mis.driver.history"
    _description = "MIS Driver History"

    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle")
    driver_id = fields.Many2one("mis.driver", string="Driver")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def remove_driver_from_vehicle(self):
        for rec in self:
            rec.vehicle_id.driver_id = None
            rec.driver_id.vehicle_ids = None
            rec.driver_id.is_vehicle_assigned = False

    def write(self, vals):
        """
        Check if 'end_date' is present in vals and remove the driver from
        the vehicle if true.
        """
        res = super().write(vals)
        if "end_date" in vals:
            self.remove_driver_from_vehicle()
        return res
