from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisDeviceInstallation(models.Model):
    _inherit = "mis.device.installation"

    total_services = fields.Integer(compute="_compute_total_numbers")

    @api.depends("installation_line_ids")
    def _compute_total_numbers(self):
        for installation in self:
            res = super()._compute_total_numbers()
            if installation.installation_line_ids:
                installation.total_services = len(
                    installation.installation_line_ids.service_id
                )
            else:
                installation.total_services = 0
            return res

    def _prepare_device_values(self, line):
        vals = super()._prepare_device_values(line)
        vals.update({"service_id": line.service_id.id})
        return vals


class MisDeviceInstallationLine(models.Model):
    _inherit = "mis.device.installation.line"

    service_id = fields.Many2one("mis.services", string="Service", readonly=False)
    sop = fields.Html(
        string="SOP", compute="_compute_service_sop", store=True, readonly=False,
    )

    @api.depends("service_id")
    def _compute_service_sop(self):
        """
        Compute the SOP field from the related service's SOP.
        """
        for line in self:
            line.sop = line.service_id.sop

    @api.onchange("sop")
    def _onchange_sop(self):
        """
        Validate that only check/uncheck actions are allowed on the SOP field.
        ses a ValidationError if other modifications are detected.
        """
        for line in self:
            db_sop = str(line._origin.sop)
            new_sop = str(line.sop)
            if line._check_sop(db_sop, new_sop):
                raise UserError(
                    _("You have no access to edit SOP in installation line.")
                )

    def _check_sop(self, db_sop, new_sop):
        """
        Compare the original and new SOP values, ignoring checked status.
        Returns True if any non-check related changes are detected.
        """
        db_text = db_sop.replace(' class="o_checked"', "")
        temp_text = new_sop.replace(' class="o_checked"', "")
        if db_text == temp_text:
            return False
        return True
