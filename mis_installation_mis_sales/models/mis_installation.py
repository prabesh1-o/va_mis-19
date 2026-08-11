from odoo import api, fields, models


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    sale_order_id = fields.Many2one("sale.order", string="Sales Order")
    remaining_deliveries = fields.Float(compute="_compute_remaining_deliveries")

    @api.depends("sale_order_id")
    def _compute_remaining_deliveries(self):
        """
        Function to compute available installations i.e. difference between quantity of total installations
         and delivered installations of all services.
        """
        for installation in self:
            installation.remaining_deliveries = 0
            if installation.sale_order_id:
                for order_line in installation.sale_order_id.order_line:
                    installation.remaining_deliveries += (
                        order_line.product_uom_qty - order_line.qty_delivered
                    )


class MisInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
