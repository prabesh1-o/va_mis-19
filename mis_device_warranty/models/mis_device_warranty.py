from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisDeviceWarranty(models.Model):
    _inherit = "mis.warranty"

    new_device_id = fields.Many2one("mis.device", string="New Device")
    device_id = fields.Many2one("mis.device", string="Device IMEI")
    warranty_package_id = fields.Many2one(
        related="device_id.warranty_package_id", readonly=True
    )
    warranty_expiry_date = fields.Date(
        related="device_id.warranty_expiry_date", readonly=True
    )
    is_bypass_warranty = fields.Boolean(string="Bypass Warranty", default=False)

    @api.constrains(
        "device_id", "warranty_expiry_date", "warranty_package_id", "is_bypass_warranty"
    )
    def _check_warranty(self):
        """
        Ensures the warranty package is set and not expired before allowing warranty creation.
        Raises:
            ValidationError: If the warranty package is not set or has already expired.
        """
        for warranty in self:
            if not warranty.warranty_package_id:
                raise ValidationError(
                    _(
                        "The warranty package is not set. You cannot create the warranty."
                    )
                )
            if not warranty.is_bypass_warranty:
                if (
                    warranty.warranty_expiry_date
                    and warranty.warranty_expiry_date < date.today()
                ):
                    raise ValidationError(
                        _(
                            "The warranty package has already expired. You cannot create the warranty."
                        )
                    )
