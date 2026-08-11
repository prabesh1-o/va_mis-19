from datetime import date,timedelta

from dateutil.relativedelta import relativedelta
from odoo import fields, models


class MisDeviceSimRechargeHistory(models.Model):
    _name = "mis.device.sim.recharge.history"
    _description = "MIS Sim Recharge History"

    name = fields.Char("Name")
    sim_id = fields.Many2one("mis.device.sim", string="Sim", required=True)
    recharge_date = fields.Date("Recharge Date", default=fields.Date.today)
    recharge_id = fields.Many2one(
        related="sim_id.sim_recharge_id", string="Recharge Pack", readonly=False
    )
    recharge_price = fields.Char(
        string="Recharge Price", related="recharge_id.recharge_price", readonly=True
    )
    recharge_expiry = fields.Date("Expiry Date", compute="_compute_expiry_date",store=True)

    def _compute_expiry_date(self):
        """Compute the expiry date based on the recharge pack's duration"""

        for history in self:
            if history.recharge_id:
                history.recharge_expiry = (
                    history.recharge_date or date.today()
                ) + relativedelta(
                    **{
                        history.recharge_id.recharge_duration_type: int(
                            history.recharge_id.recharge_duration
                        )
                    }
                )
            else:
                history.recharge_expiry = False
