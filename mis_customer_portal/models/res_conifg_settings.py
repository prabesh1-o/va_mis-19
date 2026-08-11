from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mis_server_domain = fields.Char(string="Server Domain")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            mis_server_domain=(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.mis_server_domain",)
            )
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mis.mis_server_domain", self.mis_server_domain,
        )
