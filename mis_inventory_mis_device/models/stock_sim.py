from odoo import api, fields, models


class StockSIM(models.Model):
    _name = "mis.inventory.sim"
    _description = "MIS Stock Sims"
    _rec_name = "sim_no"

    sim_no = fields.Char(
        string="SIM no", help="Enter the 10 digit phone number", required=True
    )
    sim_id = fields.Many2one("mis.device.sim", string="SIM")
    sim_carrier = fields.Selection([("ncell", "NCELL"), ("ntc", "NTC")])
    data_plan = fields.Char(string="Data Plan")
    serial_no = fields.Char(string="Serial Number")
    puk1 = fields.Char(string="PUK 1")
    puk2 = fields.Char(string="PUK 2")
    pin1 = fields.Char(string="PIN 1")
    pin2 = fields.Char(string="PIN 2")
    location_id = fields.Many2one(
        "stock.location", "Location", default=lambda self: self._default_location_id()
    )
    active = fields.Boolean(default=True)

    @api.model
    def _default_location_id(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return False
