from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisBlacklistCustomer(models.Model):
    _name = "mis.blacklist.customer"
    _description = "MIS Blacklist Customer"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Id", readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    stage = fields.Selection(
        [
            ("request", "Request"),
            ("verification", "Verification"),
            ("approval", "Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Stage",
        default="request",
        readonly=True,
        group_expand="_read_group_stage",
        tracking=True,
    )
    reason = fields.Char(string="Reason", required=True)
    request_date = fields.Date(
        string="Requested At", default=lambda self: fields.Date.today()
    )
    requested_by = fields.Many2one(
        "hr.employee",
        string="Requested By",
        default=lambda self: self.env.user.employee_id,
        required=True,
    )
    verify_date = fields.Date(string="Verified At")
    verified_by = fields.Many2one("hr.employee", string="Verified By")
    approved_date = fields.Date(string="Approved At")
    approved_by = fields.Many2one("hr.employee", string="Approved By")
    rejection_reason = fields.Char(string="Rejection Reason")
    description = fields.Html(string="Description")

    @api.model
    def _read_group_stage(self, stages, domain, order):
        """
        Retrieve and return the list of all possible stages for the 'stage' field.
        Used to group records by the 'stage' field.
        """
        return [stage[0] for stage in self._fields["stage"].selection]

    def action_btn(self):
        """
        Progress the customer record through the stages of the blacklist process.
        - From 'request' to 'verification'.
        - From 'verification' to 'approval', while setting the verification details.
        - From 'approval' to 'approved', while setting the approval details and
          marking the customer as blacklisted.
        """
        today = fields.Date.today()
        user_id = self.env.user.employee_id
        for record in self:
            if record.stage == "request":
                record.stage = "verification"
                record._create_initial_activities()
            elif record.stage == "verification":
                record.stage = "approval"
                record.verify_date = today
                record.verified_by = user_id
                record._create_initial_activities()
            elif record.stage == "approval":
                record.stage = "approved"
                record.approved_date = today
                record.approved_by = user_id
                record.customer_id.is_blacklist = True

    def action_reject(self):
        """
        Reject the blacklist request by setting the stage to 'rejected'.
        """
        for record in self:
            record.stage = "rejected"

    def action_reset(self):
        """
        Reset the blacklist request back to the initial 'request' stage.
        Clears all verification and approval detail.
        """
        for record in self:
            record.write(
                {
                    "stage": "request",
                    "verify_date": None,
                    "verified_by": None,
                    "approved_date": None,
                    "approved_by": None,
                    "rejection_reason": None,
                }
            )

    def _create_initial_activities(self):
        """
        Create initial activities for the blacklist request based on the
        verificator and approver defined in the configuration parameters.
        """
        verificator_user_id, approver_user_id = self._get_user_ids_from_config()
        if self.stage in ["verification", "approval"]:
            self._schedule_activities(
                stage=self.stage,
                verificator_user_id=verificator_user_id,
                approver_user_id=approver_user_id,
            )

    def _get_user_ids_from_config(self):
        """
        Retrieve user IDs for verificator and approver from configuration parameters.
        Converts employee IDs from configuration to user IDs.
        """
        config = self.env["ir.config_parameter"].sudo()
        verificator_employee_id = int(config.get_param("mis.verificator"))
        approver_employee_id = int(config.get_param("mis.approver"))
        verificator_user_id = (
            self.env["hr.employee"].browse(verificator_employee_id).user_id.id
        )
        approver_user_id = (
            self.env["hr.employee"].browse(approver_employee_id).user_id.id
        )
        return verificator_user_id, approver_user_id

    def _schedule_activities(self, stage, verificator_user_id, approver_user_id):
        """
        Schedule activities based on the current stage.
        """
        summary = _("Blacklist request for customer %s needs %s.") % (
            self.customer_id.name,
            "verification" if stage == "verification" else "approval",
        )
        if stage == "verification":
            user_ids = {verificator_user_id, approver_user_id}
        else:
            user_ids = {approver_user_id}
        for user_id in user_ids:
            if user_id:
                self.activity_schedule(
                    "mail.mail_activity_data_todo", user_id=user_id, summary=summary,
                )

    def _validate_blacklist_request(self, vals):
        """
        Check whether there is already an existing blacklist request.
        """
        existing_blacklist = self.search(
            [
                ("customer_id", "=", vals.get("customer_id")),
                ("stage", "!=", "rejected"),
                ("customer_id.is_blacklist", "=", True),
            ]
        )
        if existing_blacklist:
            raise UserError(_("The blacklist request is already created!"))

    @api.model_create_multi
    def create(self, vals_list):
        """
        Check whether there is already existing blacklist request.
        Override the create method to automatically generate a unique ID for each record.
        The ID is generated based on the record's primary key.
        """
        for vals in vals_list:
            self._validate_blacklist_request(vals)
        blacklists = super().create(vals_list)
        for record in blacklists:
            record.name = f"B{str(record.id).zfill(4)}"
        return blacklists
