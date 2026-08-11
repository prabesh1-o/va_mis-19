from odoo import _, fields, models
from odoo.exceptions import UserError


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    configured_status = fields.Selection(
        [("partial", "Partially Configured"), ("configured", "Configured")],
        string="Configuration Status",
        compute="_compute_configured_status",
    )

    def _create_device_from_stock(self, line):
        device_vals = self._prepare_device_values(line)
        device = self.env["mis.device"].create(device_vals)
        return device

    def _prepare_device_values(self, line):
        return {
            "installed_date": line.installation_date,
            "installation_price": line.installation_price,
            "has_tax_installation": line.has_tax_installation,
            "vehicle_id": line.vehicle_id.id,
            "renewal_price": line.renewal_price,
            "expiration_time": line.expiry_date,
            "customer_id": self.customer_id,
            "employee_ids": self.employee_ids if self.employee_ids else False,
            "state": "active",
        }

    def _compute_configured_status(self):
        """
        Compute the configuration status of the device installation.
        This method updates the 'configured_status' field for each installation record.
        """
        for installation in self:
            installation.configured_status = None
            configured = len(
                installation.installation_line_ids.filtered(lambda r: r.is_configured)
            )
            total = len(
                installation.installation_line_ids.filtered(
                    lambda r: r.state != "canceled"
                )
            )
            if configured > 0 and configured < total:
                installation.configured_status = "partial"
            elif configured == total and total > 0:
                installation.configured_status = "configured"

    def _create_sim_device_history(self, line, device):
        """
        Create a history record for the SIM device.

        Args:
            line (mis.device.installation.line): The installation line containing the SIM device data.
        """
        self.env["mis.sim.device.history"].create(
            {
                "sim_id": device.sim.id,
                "device_id": device.id,
                "vehicle_id": line.vehicle_id.id,
                "installed_date": line.installation_date,
                "customer_id": self.customer_id.id,
            }
        )

    def _create_installation_history(self, line, device):
        """
        Create an installation history record.

        Args:
            line (mis.device.installation.line): The installation line containing the installation details.
        """
        self.env["mis.device.installation.history"].create(
            {
                "device_id": device.id,
                "vehicle_id": line.vehicle_id.id,
                "installed_date": line.installation_date,
                "installation_price": line.installation_price,
                "customer_id": self.customer_id.id,
                "installation_id": self.id,
                "installed_by": self.installation_line_ids.employee_ids,
            }
        )

    def btn_configure_customer_and_devices(self):
        """
        Configure the customer and devices.

        Returns:
            super(): Calls the parent method to proceed with the next steps.
        """
        for installation in self:
            installed_devices_line = installation.installation_line_ids.filtered(
                lambda r: r.state == "installed"
            )
            for line in installed_devices_line:
                if not line.is_configured:
                    installed_device = self._create_device_from_stock(line)
                    self._create_sim_device_history(line, installed_device)
                    self._create_installation_history(line, installed_device)
                    line.is_configured = True
        return super().btn_configure_customer_and_devices()


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    def btn_update_installation_state(self):
        """
        Validates that the required device information (device, SIM, and vehicle).
        Returns:
            super(): Calls the parent method to proceed with the update.
        """
        for line in self:
            if not (line.stock_device_id and line.stock_sim_id):
                raise UserError(
                    _("Add the device information first i.e. Devices or SIM ")
                )

        return super().btn_update_installation_state()
