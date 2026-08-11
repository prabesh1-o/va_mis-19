from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_note = fields.Html(string="Terms & Conditions")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            sale_note=(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.sale_note", default="")
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mis.sale_note", self.sale_note
        )
