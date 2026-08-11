from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    warranty_id = fields.Many2one("mis.warranty", string="Warranty")

    def action_view_warranty(self):
        """
        Opens the form view for the warranty associated with the current device.
        Returns:
            dict: An action dictionary to display the form view of the warranty
                  record linked to the device.
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        action = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
        action["view_mode"] = "form"
        action["res_id"] = self.warranty_id.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action
