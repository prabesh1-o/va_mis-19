from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisDevice(models.Model):
    _inherit = "mis.device"

    warranty_id = fields.One2many("mis.warranty", "device_id", string="Warranty")
    warranty_count = fields.Integer(compute="_compute_warranty_count")
    warranty_package_id = fields.Many2one(
        "mis.warranty.package", string="Warranty Package"
    )
    warranty_expiry_date = fields.Date(
        compute="_compute_warranty_coverage", string="Warranty Expiry", store=True
    )
    is_warranty_return = fields.Boolean(string="Warranty Return", default=False)
    is_warranty_replaced = fields.Boolean(string="Warranty Replaced", default=False)

    def _compute_warranty_count(self):
        """
        Calculates the number of warranties associated with each device
        and updates the warranty_count field.
        Sets:
            warranty_count (int): The total number of warranties linked to the device.
        """
        for device in self:
            device.warranty_count = len(device.warranty_id)

    def action_view_warranty(self):
        """
        Opens the warranty view for the current device with a specified XML ID if provided.
        Returns:
            dict: An action dictionary to display the warranty records in tree, kanban,
            and form views, filtered by the current device.
            False: If no XML ID is provided in the context.
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(
                    self.env.context, default_device_id=self.id, group_by=False
                ),
                domain=[("device_id", "=", self.id)],
                view_mode="tree,kanban,form",
                views=[(False, "tree"), (False, "kanban"), (False, "form")],
            )
            return res
        return False

    @api.depends(
        "warranty_package_id",
        "warranty_package_id.warranty_period",
        "warranty_package_id.warranty_period_type",
    )
    def _compute_warranty_coverage(self):
        """
        Computes the warranty coverage period based on the warranty package
        and installation date.
        Raises:
            ValidationError: If the installation date is not set when a warranty package is assigned.
        Sets:
            warranty_expiry_date (date): The calculated expiration date of the warranty
            based on the warranty period and type.
        """
        for device in self:
            if not device.warranty_expiry_date:
                if device.warranty_package_id and not device.installed_date:
                    raise ValidationError(
                        _(
                            "The installation date is not set. First set the installation date."
                        )
                    )
                else:
                    if device.warranty_package_id:
                        period = device.warranty_package_id.warranty_period
                        warranty_type = device.warranty_package_id.warranty_period_type
                        period_map = {
                            "days": {"days": period},
                            "months": {"months": period},
                            "years": {"years": period},
                        }
                        if warranty_type in period_map:
                            device.warranty_expiry_date = (
                                device.installed_date
                                + relativedelta(**period_map[warranty_type])
                            )
                    else:
                        device.warranty_expiry_date = None
