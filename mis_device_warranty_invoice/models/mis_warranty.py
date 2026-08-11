from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError


class MisDeviceWarranty(models.Model):
    _inherit = "mis.warranty"

    invoice_id = fields.Many2one("account.move", string="Invoice")

    def btn_create_invoice(self):
        """
        Creates an invoice for the warranty if not already created.
        Raises:
            UserError: If an invoice has already been created for the warranty.
        """
        for warranty in self:
            if warranty.invoice_id:
                raise UserError(_("Invoice is already created!"))
            invoice = self.env["account.move"].create(
                {
                    "partner_id": warranty.customer_id.id,
                    "move_type": "out_invoice",
                    "invoice_date": date.today(),
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": f"Warranty({warranty.device_id.imei_no})",
                                "quantity": 1.0,
                                "price_unit": warranty.charge,
                            },
                        )
                    ],
                }
            )
            warranty.invoice_id = invoice.id
            warranty.invoice_id.warranty_id = warranty.id

    def action_view_invoice(self):
        """
        Opens the form view for the invoice associated with the current warranty.
        Returns:
            dict: An action dictionary to display the form view of the invoice
                  record linked to the warranty.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        action["domain"] = [("warranty_id", "=", self.id)]
        action["view_mode"] = "form"
        action["res_id"] = self.invoice_id.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action
