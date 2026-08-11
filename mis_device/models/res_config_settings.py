import ast

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sim_recharge_expiry_days_count = fields.Integer(string="Expires In")
    responsible_sim_assignees = fields.Many2many(
        "res.users",
        domain=lambda self: [("group_ids", "in", self._get_sim_group_ids())],
    )

    def _get_sim_group_ids(self):
        group_ids = [
            self.env.ref("mis_device.group_mis_device_admin").id,
            self.env.ref("mis_device.group_mis_device_manager").id,
        ]
        return group_ids

    @api.model
    def get_values(self):
        """
        Fetch stored configuration settings.

        This method fetches and returns values from the `ir.config_parameter` model,
        ensuring that system parameters are correctly loaded into the settings UI.

        Returns:
            dict: A dictionary of configuration values for the settings view.
        """
        res = super(ResConfigSettings, self).get_values()
        expiry_days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sim_recharge_expiry_days_count", default=3)
        )
        assignees = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("responsible_sim_assignees", "[]")
        )
        try:
            assignees = ast.literal_eval(assignees)
        except Exception:
            assignees = []

        res.update(
            {
                "sim_recharge_expiry_days_count": expiry_days_count,
                "responsible_sim_assignees": assignees,
            }
        )
        return res

    def set_values(self):
        """
        Set or update configuration settings.

        This method stores values set in the UI into the `ir.config_parameter` model,
        ensuring that changes persist beyond the current session.
        """
        super(ResConfigSettings, self).set_values()
        params = {
            "sim_recharge_expiry_days_count": self.sim_recharge_expiry_days_count,
            "responsible_sim_assignees": str(self.responsible_sim_assignees.ids),
        }
        for key, value in params.items():
            self.env["ir.config_parameter"].sudo().set_param(key, value)
