from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mis_renewal_completion_days_count = fields.Integer(string="Renewal Days Count")
    mis_renewal_expiry_days_count = fields.Integer(string="Expiry Days Count")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            mis_renewal_completion_days_count=int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.mis_renewal_completion_days_count", default=7)
            ),
            mis_renewal_expiry_days_count=int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.mis_renewal_expiry_days_count", default=7)
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = {
            "mis.mis_renewal_completion_days_count": self.mis_renewal_completion_days_count,
            "mis.mis_renewal_expiry_days_count": self.mis_renewal_expiry_days_count,
        }
        for key, value in params.items():
            self.env["ir.config_parameter"].sudo().set_param(key, value)
