from datetime import date

from odoo import api, fields, models


class MisDevice(models.Model):
    _name = "mis.device"
    _description = "MIS Devices"
    _rec_name = "imei_no"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    imei_no = fields.Char(string="IMEI no.", tracking=True, required=True)
    installed_date = fields.Date(string="Installation Date", tracking=True)
    expiration_time = fields.Date(string="Expiry Date", tracking=True)
    sim = fields.Many2one("mis.device.sim", string="SIM")
    active = fields.Boolean(default=True, string="Live")
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        string="Status",
        default="active",
    )
    customer_id = fields.Many2many(
        "res.partner",
        "customer_device_rels",
        "device_id",
        "customer_id",
        string="Customer",
        tracking=True,
        domain="[('is_customer','=',True)]",
    )
    customer_assigned_ids = fields.Many2many(
        "res.partner",
        string="Customer Assigned",
        tracking=True,
        domain="[('is_customer','=',True)]",
    )
    installation_price = fields.Monetary(
        currency_field="company_currency_id", group_operator="sum"
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")

    @api.model
    def change_device_state(self):
        """
        Set device state as inactive if their expiration date has passed.
        """
        devices = self.search(
            [("expiration_time", "<", date.today()), ("state", "=", "active")]
        )
        for device in devices:
            device.state = "inactive"

    def action_view_customers(self):
        """
        Open a view showing customers linked to this device.

        Returns:
            `dict`: An action dictionary to open the customer view.
        """
        partner_ids = list(set(self.customer_id.ids + self.customer_assigned_ids.ids))
        return {
            "name": "Customers",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,tree,form",
            "res_model": "res.partner",
            "domain": [("id", "in", partner_ids)],
        }
