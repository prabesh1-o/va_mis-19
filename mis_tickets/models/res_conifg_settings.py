from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mis_tickets_completions_days_count = fields.Integer(string="Ticket Days Count")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            mis_tickets_completions_days_count=int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mis.mis_tickets_completions_days_count", default=7)
            )
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "mis.mis_tickets_completions_days_count",
            self.mis_tickets_completions_days_count,
        )
