from odoo import api, fields, models


class MisDeviceRenewalHistory(models.Model):
    _name = "mis.device.renewal.history"
    _description = "MIS Device Renewal History"

    name = fields.Char(string="Name", readonly=True)
    device_id = fields.Many2one("mis.device", string="Device", tracking=True)
    renewal_date = fields.Date(string="Renewal Date", default=fields.Date.context_today)
    renewal_package_id = fields.Many2one(
        related="device_id.renewal_package_id", string="Renewal Package", store=True
    )
    customer_ids = fields.Many2many(
        related="device_id.customer_id", string="Customer", readonly=True
    )
    company_currency_id = fields.Many2one(related="device_id.company_currency_id")
    renewal_price = fields.Monetary(
        currency_field="company_currency_id", string="Rate", store=True,
    )
    old_expiry_date = fields.Date(string="Old Expiry Date")
    expiry_date = fields.Date(string="New Expiry Date")
    payment_date = fields.Date(string="Payment Date")
    renewal_id = fields.Many2one("mis.device.renewal", string="Renewal Ticket")
    grace_period_days_count = fields.Integer(string="Total Grace Period Days")

    def _generate_name(self):
        """
        Generates a name for the renewal history based on its ID.

        The generated name follows the format 'RH' followed by the history ID,
        zero-padded to four digits.
        """
        for history in self:
            name = f"RH{str(history.id).zfill(4)}"
            return name

    @api.model_create_multi
    def create(self, vals_list):
        """
        Creates multiple renewal history records and assigns a generated name to each.

        The name for each record is generated using the `_generate_name` method
        and assigned after creation.
        """
        histories = super().create(vals_list)
        for history in histories:
            history.name = history._generate_name()
        return history
