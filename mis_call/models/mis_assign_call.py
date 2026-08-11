from odoo import api, fields, models


class MisCallAssign(models.Model):
    _name = "mis.assign.call"
    _description = "MIS Assign Call"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Id", readonly=True)
    assignee = fields.Many2one("hr.employee", string="Assignee", tracking=True)
    assigned_by = fields.Many2one("hr.employee", string="Assigned By")
    is_resolved = fields.Boolean(
        string="Resolved",
        default=False,
        compute="_compute_is_resolved",
        store=True,
        recursive=True,
        readonly=False,
    )
    active = fields.Boolean(string="Active", default=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "Progress"),
            ("extended", "Extended"),
            ("completed", "Completed"),
        ],
        default="draft",
        group_expand="_read_group_state",
        tracking=True,
    )
    deadline_date = fields.Date(string="Deadline")
    has_follow_up = fields.Boolean(string="Follow Up", default=False)
    follow_up_deadline = fields.Date(string="Next Deadline")
    tag_ids = fields.Many2many("mis.call.tags", string="Tags")
    child_call_id = fields.Many2one("mis.assign.call")
    parent_call_id = fields.Many2one("mis.assign.call")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    campaign_id = fields.Many2one("mis.call.campaign", string="Campaign", required=True)
    batch_id = fields.Many2one("mis.call.batch", string="Batch")
    source_model_id = fields.Many2one("ir.model", string="Model")
    source_record_id = fields.Integer(string="Record ID")
    call_duration = fields.Float(string="Duration")
    number = fields.Char(
        string="Phone Number", readonly=False, compute="_compute_phn_no"
    )
    time = fields.Datetime(string="Time", tracking=True)
    response = fields.Char(string="Response")
    description = fields.Html(string="Description")

    @api.model
    def _read_group_state(self, states, domain, order):
        """
        Retrieve a list of available states from the state field's selection.
        """
        return [state[0] for state in self._fields["state"].selection]

    @api.onchange("assignee")
    def onchange_assignee(self):
        """
        Sets assigned by default when the assignee is set.
        """
        current_user = self.env.user
        for call in self:
            call.assigned_by = current_user.employee_id

    @api.depends("child_call_id.is_resolved")
    def _compute_is_resolved(self):
        """
        Resolve parent call if child call is resolved.
        """
        for call in self:
            if call.child_call_id and call.child_call_id.is_resolved:
                call.state = "completed"
                call.is_resolved = True

    def btn_confirm(self):
        """
        Button to change state of call
        """
        for call in self:
            if call.state == "draft":
                call.state = "progress"
                call.time = fields.Datetime.now()

    def btn_resolve(self):
        """
        Button to resolve call
        """
        for call in self:
            call.state = "completed"
            call.is_resolved = True

    @api.onchange("customer_id", "number")
    @api.depends("customer_id", "number")
    def _compute_phn_no(self):
        for call in self:
            if call.customer_id:
                if call.customer_id.mobile:
                    call.number = call.customer_id.mobile
                else:
                    call.customer_id.mobile = call.number

    def btn_create_child_call(self):
        """
        Create a new call for the unresolved call.
        """
        for record in self:
            new_call = self.create(
                {
                    "assignee": record.assignee.id,
                    "assigned_by": record.assigned_by.id,
                    "deadline_date": record.follow_up_deadline,
                    "customer_id": record.customer_id.id,
                    "campaign_id": record.campaign_id.id,
                    "source_model_id": record.source_model_id.id,
                    "source_record_id": record.source_record_id,
                    "parent_call_id": record.id,
                    "tag_ids": [(6, 0, record.tag_ids.ids)],
                    "number": record.number,
                    "description": record.description,
                }
            )
            record.child_call_id = new_call.id
            record.state = "extended"
            return record.with_context(res_id=new_call.id).btn_view_call()

    def btn_view_call(self):
        """
        Button to view associated calls.
        """
        self.ensure_one()
        res_id = self.env.context.get("res_id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "mis.assign.call",
            "view_mode": "form",
            "res_id": res_id,
            "target": "current",
        }

    def btn_view_related_record(self):
        """
        Button to view related record of call.
        """
        for call in self:
            return {
                "type": "ir.actions.act_window",
                "res_model": call.source_model_id.model,
                "view_mode": "form",
                "res_id": call.source_record_id,
                "target": "current",
            }

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to generate a custom name for each call upon creation.
        """
        calls = super().create(vals_list)
        for call in calls:
            call.name = f"C{str(call.id).zfill(4)}"
        return calls


class MisCallTags(models.Model):
    _name = "mis.call.tags"
    _description = "MIS Call Tags"

    name = fields.Char(string="Name")
    color = fields.Char(string="color")
    _sql_constraints = [
        ("name_uniq", "unique (name)", "A tag with the same name already exists."),
    ]
