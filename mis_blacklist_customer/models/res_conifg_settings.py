from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    verificator = fields.Many2one("hr.employee", string="Verified By")
    approver = fields.Many2one("hr.employee", string="Approved By")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env["ir.config_parameter"].sudo()

        verificator_id = icp.get_param("mis.verificator")
        approver_id = icp.get_param("mis.approver")

        res.update(
            verificator=int(verificator_id) if verificator_id else False,
            approver=int(approver_id) if approver_id else False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = {
            "mis.verificator": self.verificator.id if self.verificator else False,
            "mis.approver": self.approver.id if self.approver else False,
        }
        for key, value in params.items():
            self.env["ir.config_parameter"].sudo().set_param(key, value)
