from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    renewal_id = fields.Many2one("mis.device.renewal", string="Renewal")
    renewal_count = fields.Integer(compute="_compute_renewal_count")

    def _compute_renewal_count(self):
        for invoice in self:
            invoice.renewal_count = len(invoice.renewal_id)

    def return_action_to_open(self):
        """
        To open action while clicking in the button box,
        gets external id from context
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            action = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            if self.renewal_count == 1:
                action["view_mode"] = "form"
                action["res_id"] = self.renewal_id.id
                if "views" in action:
                    action["views"] = [
                        (view_id, view_type)
                        for view_id, view_type in action["views"]
                        if view_type == "form"
                    ]
            return action
        return False
