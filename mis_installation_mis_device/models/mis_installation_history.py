from odoo import fields, models


class MisDeviceInstallationHistory(models.Model):
    _name = "mis.device.installation.history"
    _description = "MIS Device Installation History"

    device_id = fields.Many2one("mis.device", string="Device")
    vehicle_id = fields.Many2one("mis.vehicle", string="Vehicle No.")
    installed_date = fields.Date(
        string="Installed Date", default=fields.Date.context_today
    )
    company_currency_id = fields.Many2one(related="device_id.company_currency_id")
    installation_price = fields.Monetary(
        currency_field="company_currency_id", string="Price", store=True,
    )
    customer_id = fields.Many2one(
        "res.partner", domain="[('is_customer','=',True)]", readonly=True
    )
    installation_id = fields.Many2one("mis.device.installation", string="Installation")
    installed_by = fields.Many2many("hr.employee", string="Installed by")
