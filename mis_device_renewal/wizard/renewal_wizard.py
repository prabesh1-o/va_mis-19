from odoo import _, fields, models
from odoo.exceptions import UserError


class MisDeviceRenewalWizard(models.TransientModel):
    _name = "mis.device.renewal.wizard"
    _description = "MIS Device Renewal Wizard"

    renewal_id = fields.Many2one("mis.device.renewal", string="Renewal", readonly=True)
    customer_ids = fields.Many2many(related="renewal_id.customer_ids", readonly=True)
    devices = fields.Many2many(related="renewal_id.device_ids", readonly=True)
    device_ids = fields.Many2many(
        "mis.device", string="Devices", domain="[('id', 'in', devices)]",
    )

    def action_break_renewal_card(self):
        """
        Creates a new renewal card with selected devices and removes them from the original card.
        """
        for record in self:
            renewal_id = record.renewal_id
            if renewal_id.stage_id.sequence not in (0, 1, 2):
                raise UserError(
                    _(
                        "Card can be broken only"
                        " in Open, Idle and Grace Period stages"
                    )
                )
            new_renewal = self.env["mis.device.renewal"].create(
                {
                    "stage_id": renewal_id.stage_id.id,
                    "customer_ids": [(6, 0, renewal_id.customer_ids.ids)],
                    "employee_ids": [(6, 0, renewal_id.employee_ids.ids)],
                    "tag_ids": [(6, 0, renewal_id.tag_ids.ids)],
                    "device_ids": [(6, 0, record.device_ids.ids)],
                }
            )
            renewal_id.write(
                {"device_ids": [(3, device.id) for device in record.device_ids]}
            )
            return new_renewal
