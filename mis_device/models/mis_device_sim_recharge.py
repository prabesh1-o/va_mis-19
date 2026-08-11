from odoo import fields, models


class MisDeviceSimRecharge(models.Model):
    _name = "mis.device.sim.recharge"
    _description = "MIS Device SIM Recharge"

    name = fields.Char("Name", required=True)
    sim_ids = fields.One2many("mis.device.sim", "sim_recharge_id", "Recharge")
    recharge_duration = fields.Char("Recharge Duration", required=True)
    recharge_duration_type = fields.Selection(
        selection=[("days", "Days"), ("months", "Months"), ("years", "Years"),],
        string="Recharge Duration Type",
        required=True,
    )
    recharge_price = fields.Char("Recharge Price", required=True)
