from odoo import _ as getTextAlias
from odoo import api, fields, models
from odoo.exceptions import UserError


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        compute="_compute_customer_and_installation_line_id",
        store=True,
        readonly=False,
    )

    @api.depends("sale_order_id", "remaining_deliveries")
    def _compute_customer_and_installation_line_id(self):
        """
        Function to compute customer_id and installations when sale_order is set.
        Parameter:
            self i.e. installations
        Return:
            Returns nothing but sets customer_id and installations of the current sale_order_id
             if sale_order is present.
        """
        for installation in self:
            if installation.sale_order_id:
                if installation.remaining_deliveries > 0:
                    installation.customer_id = installation.sale_order_id.partner_id
                    installation.installation_line_ids = None
                    installation_lines = []
                    for order_line in installation.sale_order_id.order_line:
                        if order_line.product_id.service_id.is_installable:
                            for _ in range(
                                int(
                                    order_line.product_uom_qty
                                    - order_line.qty_delivered
                                )
                            ):
                                installation_lines.append(
                                    (
                                        0,
                                        0,
                                        {
                                            "installation_id": installation.id,
                                            "service_id": order_line.product_id.service_id.id,
                                            "installation_price": order_line.price_unit_tax,
                                            "renewal_price": order_line.renewal_price,
                                        },
                                    )
                                )
                    installation.installation_line_ids = installation_lines
                else:
                    raise UserError(
                        getTextAlias(
                            "Every service has already been delivered, You cannot create Installation Order."
                        )
                    )
            else:
                installation.customer_id = None


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    has_tax_installation = fields.Boolean(string="Installation Tax", default=False)

    def btn_update_installation_state(self):
        if self.installation_id.sale_order_id:
            if self._context.get("is_installation_btn", False):
                self.validate_sales_order_delivered_qty()
        return super().btn_update_installation_state()

    def validate_sales_order_delivered_qty(self):
        for line in self:
            sale_order = line.sale_order_line_id
            if sale_order.product_uom_qty == sale_order.qty_delivered:
                raise UserError(
                    getTextAlias(
                        "Every ordered quantity has already been delivered. "
                        "Please confirm through sales order."
                    )
                )

    def write(self, vals):
        if "state" in vals and self.installation_id.sale_order_id:
            self.validate_sales_order_delivered_qty()
        return super().write(vals)
