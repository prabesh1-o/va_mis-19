from odoo import _, fields, models
from odoo.exceptions import UserError


class MisDeviceWarranty(models.Model):
    _inherit = "mis.warranty"

    installation_id = fields.Many2one(
        "mis.device.installation", string="Installation Id"
    )

    def action_view_installation_order(self):
        """
        Opens the form view for the installation order associated with the warranty.
        Returns:
            dict: An action dictionary to display the form view of the installation
                  order linked to the warranty.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_device_installation.mis_installation_action"
        )
        action["domain"] = [("warranty_id", "=", self.id)]
        action["view_mode"] = "form"
        action["res_id"] = self.installation_id.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action

    def _get_stock_sim_id(self):
        stock_sim_id = (
            self.env["mis.inventory.sim"]
            .with_context(active_test=False)
            .search([("sim_no", "=", self.device_id.sim.sim_no)])
        )
        return stock_sim_id

    def btn_create_installation_order(self):
        """
        Creates an installation order for the warranty if one does not already exist.
        Raises:
            UserError: If an installation order has already been created for the warranty.
        """
        self.ensure_one()
        if self.installation_id:
            raise UserError(_("Installation order is already created!"))
        if self.new_stock_device_id:
            self.device_id.write(
                {
                    "active": False,
                    "state": "inactive",
                    "is_warranty_return": True,
                    "is_warranty_replaced": False,
                }
            )

        installation_order = self.env["mis.device.installation"].create(
            {
                "customer_id": self.customer_id.id,
                "warranty_id": self.id,
                "installation_line_ids": [
                    (0, 0, self._prepare_installation_lines_warranty())
                ],
            }
        )
        self.installation_id = installation_order.id

    def _prepare_installation_lines_warranty(self):
        return {
            "service_id": self.device_id.service_id.id,
            "vehicle_id": self.device_id.vehicle_id.id,
            "stock_sim_id": self._get_stock_sim_id().id,
            "expiry_date": self.device_id.expiration_time,
            "renewal_price": self.device_id.renewal_price,
            "installation_price": self.device_id.installation_price,
            "warranty_package": self.device_id.warranty_package_id.id,
            "warranty_expiry": self.device_id.warranty_expiry_date,
        }
