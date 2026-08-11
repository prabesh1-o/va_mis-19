from datetime import date

from odoo import api, fields, models


class MisDeviceWarranty(models.Model):
    _name = "mis.warranty"
    _description = "MIS Device Warranty"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Id", readonly=True)
    stage = fields.Selection(
        [
            ("claimed", "Claimed"),
            ("verification", "Verification"),
            ("extraction", "Extraction"),
            ("received", "Received"),
            ("resolved", "Resolved"),
            ("cancelled", "Cancelled"),
        ],
        string="Stage",
        default="claimed",
        group_expand="_read_group_stage",
        tracking=True,
    )
    is_extracted = fields.Boolean(string="Extracted", default=False)
    extraction_date = fields.Date(string="Extraction Date", tracking=True)
    received_date = fields.Date(string="Received Date", tracking=True)
    verified_by = fields.Many2one("hr.employee", string="Verified By", tracking=True)
    verification_date = fields.Datetime(string="Verification Date", tracking=True)
    employee_ids = fields.Many2many("hr.employee", string="Assignee", tracking=True)
    resolution = fields.Selection(
        [("repaired", "Repaired"), ("replaced", "Replaced")],
        string="Resolution",
        tracking=True,
    )
    resolution_date = fields.Date(string="Resolved Date", tracking=True)
    charge = fields.Monetary(
        currency_field="company_currency_id", string="Price", tracking=True
    )
    customer_id = fields.Many2one("res.partner", string="Customer")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    description = fields.Html(string="Description")

    @api.model
    def _read_group_stage(self, stages, domain, order=None):
        """
        Groups records by stage and returns the list of available stage values.
        Returns:
            list: A list of stage values extracted from the selection field.
        """
        return [stage[0] for stage in self._fields["stage"].selection]

    @api.onchange("stage")
    def set_date(self):
        """
        Sets the appropriate date fields based on the current stage of the warranty.
        Updates:
            received_date (date): Set to today's date if the stage is "received" and
            if device is extracted.
            resolution_date (date): Set to today's date if the stage is "received".
        """
        today = date.today()
        for warranty in self:
            if warranty.stage == "verification":
                warranty.verification_date = fields.Datetime.now()
            if warranty.stage == "received" and warranty.is_extracted:
                warranty.received_date = today
            if warranty.stage == "resolved":
                warranty.resolution_date = today

    @api.onchange("is_extracted")
    def set_extraction_date(self):
        for warranty in self:
            if warranty.is_extracted:
                warranty.extraction_date = date.today()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the create method to generate and assign a unique
        warranty name for each newly created warranty depending on Id.
        """
        warranties = super().create(vals_list)
        for warranty in warranties:
            warranty.name = f"W{str(warranty.id).zfill(4)}"
        return warranties


class MisWarrantyPackage(models.Model):
    _name = "mis.warranty.package"
    _description = "MIS Warranty Package"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Package Name", required=True)
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    warranty_type = fields.Many2one(
        "mis.warranty.type", string="Warranty Type", required=True
    )
    warranty_period = fields.Integer(string="Period", required=True)
    warranty_period_type = fields.Selection(
        selection=[("days", "Days"), ("months", "Months"), ("years", "Years")],
        required=True,
        default="years",
    )
    warranty_period_with_type = fields.Char(
        string="Warranty Period",
        compute="_compute_complete_warranty_period",
        store=True,
        tracking=True,
    )
    description = fields.Html(string="Description")

    @api.depends("warranty_period", "warranty_period_type")
    def _compute_complete_warranty_period(self):
        """
        Computes the complete warranty period with its type for each package.
        Sets:
            warranty_period_with_type (str): A formatted string combining the
             warranty period and type, or None if either is missing.
        """
        for package in self:
            package.warranty_period_with_type = (
                f"{package.warranty_period} {package.warranty_period_type}"
                if package.warranty_period and package.warranty_period_type
                else None
            )


class MisWarrantyType(models.Model):
    _name = "mis.warranty.type"
    _description = "MIS Warranty Type"

    name = fields.Char(string="Name")
