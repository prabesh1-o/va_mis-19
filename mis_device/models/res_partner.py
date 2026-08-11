from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    device_ids = fields.Many2many(
        "mis.device",
        "customer_device_rels",
        "customer_id",
        "device_id",
        string="Devices",
    )
    installed_device_history_ids = fields.Many2many(
        "mis.installed.device.history",
        string="Installed Devices",
        compute="_compute_installed_devices_history",
        store=True,
        readonly=False,
    )
    is_customer = fields.Boolean(string="Customer", default=False)
    current_company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company
    )
    company_currency_id = fields.Many2one(
        related="current_company_id.currency_id", string="Company currency"
    )
    total_amount_residual = fields.Monetary(
        compute="_compute_total_residual",
        string="Total Amount Due",
        currency_field="company_currency_id",
    )
    device_count = fields.Integer(
        string="Total Devices", compute="_compute_device_count", store=True
    )

    def _compute_total_residual(self):
        """
        Compute the total outstanding amount for the partner.

        Updates:
            total_amount_residual (float): Sum of all residual invoice amounts.
        """
        for partner in self:
            invoices = self.env["account.move"].search([
                ("partner_id", "=", partner.id)
            ])
            total_residual = sum(invoices.mapped("amount_residual"))
            partner.total_amount_residual = total_residual

    @api.depends("device_ids")
    def _compute_device_count(self):
        """
        Compute the total number of devices associated with the partner.

        Updates:
            device_count (int): The count of devices linked to the partner.
        """
        for partner in self:
            partner.device_count = len(partner.device_ids)

    @api.depends("device_ids")
    def _compute_installed_devices_history(self):
        """
        Compute the history of installed devices for each partner.

        This method checks the difference between currently associated devices(`device_ids`)
        and previously installed devices histories(`installed_device_history_ids`).
        If new devices are found, it creates corresponding history records and
        updates the installed device history. Finally, it triggers the update of
        past device history flags.
        """
        installed_devices_history = self.env["mis.installed.device.history"]
        for partner in self:
            current_devices = partner.device_ids
            new_devices = (
                current_devices - partner.installed_device_history_ids.device_id
            )
            if new_devices:
                vals_list = [
                    {"device_id": device.id, "customer_id": partner.id,}
                    for device in new_devices
                ]
                new_installed_records = installed_devices_history.create(vals_list)
                if new_installed_records:
                    partner.installed_device_history_ids = [
                        (4, rec.id) for rec in new_installed_records
                    ]
            self._set_flag_past_devices_history()

    def _set_flag_past_devices_history(self):
        """
        Update the active status of past installed devices histories.

        This method identifies devices that were previously installed but are
        no longer associated with the partner (`device_ids`). It updates the
        corresponding history records by marking the flag false.
        """
        for partner in self:
            all_active_devices = partner.installed_device_history_ids.filtered(
                "is_active"
            ).mapped("device_id")
            past_devices = all_active_devices - partner.device_ids
            if past_devices:
                past_devices_history = partner.installed_device_history_ids.filtered(
                    lambda d: d.device_id in past_devices
                )
                if past_devices_history:
                    past_devices_history.write({"is_active": False})
