from odoo import fields, models


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    is_repaired = fields.Boolean(string="Repaired", compute="_compute_repaired_status",)
    warranty_id = fields.Many2one("mis.warranty", string="Warranty")

    def _compute_repaired_status(self):
        """
        Validates and updates the warranty status of installations.
        """
        for installation in self:
            if installation.warranty_id.resolution == "repaired":
                installation.is_repaired = True

    def _prepare_device_values(self, line):
        vals = super()._prepare_device_values(line)
        vals.update(
            {
                "warranty_expiry_date": line.warranty_expiry,
                "warranty_package_id": line.warranty_package.id,
            }
        )
        return vals


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    # Two fields are used to store the data of warranty of old device
    warranty_expiry = fields.Date()
    warranty_package = fields.Many2one("mis.warranty.package")
