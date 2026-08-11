from odoo import api, fields, models


class DeviceIMEI(models.Model):
    _name = "mis.inventory.device"
    _rec_name = "imei_no"

    imei_no = fields.Char(string="IMEI no.", required=True)
    device_id = fields.Many2one("mis.device", string="Device")
    product_id = fields.Many2one(
    "product.product",
    string="Product Name",
    domain="[('type', '=', 'consu')]",
    store=True,
    )
    device_model_id = fields.Many2one("mis.product.model", string="Model")
    location_id = fields.Many2one(
        "stock.location",
        string="Location",
        domain="[('usage','=','internal')]",
        default=lambda self: self._get_default_location(),
    )

    active = fields.Boolean(default=True)

    @api.model
    def _get_default_location(self):
        warehouse = self.env["stock.warehouse"].search([], limit=1)
        if warehouse:
            return warehouse.lot_stock_id
        return False
