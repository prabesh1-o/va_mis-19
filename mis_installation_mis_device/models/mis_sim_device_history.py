from odoo import fields, models


class MisSimDeviceHistory(models.Model):
    _name = "mis.sim.device.history"
    _description = "MIS SIM Device History"

    sim_id = fields.Many2one("mis.device.sim", string="SIM")
    customer_id = fields.Many2one(
        "res.partner", domain="[('is_customer','=',True)]", readonly=True
    )
    device_id = fields.Many2one("mis.device", string="Device")
    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle No.")
    installed_date = fields.Date(
        string="Installed Date", default=fields.Date.context_today
    )
