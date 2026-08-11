from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MISDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    warranty_delivery_count = fields.Integer(related="warranty_id.delivery_count")

    def btn_configure_customer_and_devices(self):
        super().btn_configure_customer_and_devices()
        for line in self:
            if line.warranty_id and line.warranty_id.resolution == "replaced":
                pickings = line.warranty_id.picking_ids.filtered(
                    lambda s: s.state == "done" and s.picking_type_code == "outgoing"
                )
                if not pickings:
                    raise ValidationError(
                        _("Please validate the Delivery from Inventory")
                    )

    def _prepare_device_values(self, line):
        vals = super()._prepare_device_values(line)
        if self.warranty_id and self.warranty_id.new_stock_device_id:
            vals.update(
                {"is_warranty_replaced": True, "is_warranty_return": False,}
            )
        return vals

    def action_view_delivery_warranty(self):
        """
        Show delivery button in mis device installation from warranty
        """
        self.ensure_one()
        if self.warranty_id:
            return self.warranty_id.action_view_delivery()


class MisDeviceInstallationline(models.Model):
    _inherit = "mis.device.installation.line"

    def btn_update_installation_state(self):
        super().btn_update_installation_state()
        for line in self:
            for warranty in line.installation_id.warranty_id:
                warranty.picking_ids.action_confirm()
                valid_moves = warranty.picking_ids.filtered(
                    lambda move: move.state not in ["done", "cancel"]
                )
                if valid_moves:
                    for move in valid_moves:
                        self._validate_product_availability(move)
