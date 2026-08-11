from odoo import fields, models


class MisDevice(models.Model):
    _inherit = "mis.device"

    has_tax_installation = fields.Boolean(string="Installation Tax", default=False)
    installation_tax_string = fields.Char(compute="_compute_installation_tax_string")
    installation_history_ids = fields.One2many(
        "mis.device.installation.history", "device_id", string="Installation History"
    )
    installation_history_count = fields.Integer(
        compute="_compute_device_installation_history_count"
    )
    employee_ids = fields.Many2many("hr.employee", string="Installed By")

    def _compute_installation_tax_string(self):
        for device in self:
            if device.has_tax_installation:
                price = device.installation_price + (
                    (device.tax_id.amount / 100) * device.installation_price
                )
                device.installation_tax_string = (
                    f"(= Rs {round(price, 2):,} Incl. Taxes)"
                )
            else:
                device.installation_tax_string = None

    def _compute_device_installation_history_count(self):
        for device in self:
            device.installation_history_count = len(device.installation_history_ids)

    def return_action_to_open(self):
        """
        To open action while clicking in the button box,
        gets external id from context
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(
                    self.env.context, default_device_id=self.id, group_by=False
                ),
                domain=[("device_id", "=", self.id)],
            )
            return res
        return False
