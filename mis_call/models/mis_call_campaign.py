from odoo import _, api, fields, models


class MisCallCampaign(models.Model):
    _name = "mis.call.campaign"
    _description = "MIS Call Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Campaign", required=True)
    description = fields.Html(string="Description")
    active = fields.Boolean(string="Active", default=True)
    manager = fields.Many2one(
        "hr.employee", string="Manager", default=lambda self: self.env.user.employee_id,
    )
    tag_ids = fields.Many2many("mis.call.campaign.tags", string="Tags")
    assignees = fields.Many2many(
        "hr.employee",
        string="Campaign Assignees",
        default=lambda self: [(4, self.env.user.employee_id.id)],
    )
    start_date = fields.Date(string="Planned Date")
    end_date = fields.Date()
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    call_count = fields.Integer(
        compute="_compute_assigned_call_count", string="Call Count", store=False
    )
    stage = fields.Selection(
        [("progress", "In Progress"), ("completed", "Completed")],
        string="Stage",
        group_expand="_read_group_stage",
        default="progress",
    )
    call_batch_ids = fields.One2many("mis.call.batch", "campaign_id", string="Batch")
    assigned_call_ids = fields.One2many(
        "mis.assign.call", "campaign_id", string="Assigned Calls"
    )

    @api.model
    def _read_group_stage(self, stages, domain, order=None):
        """
        Retrieve a list of available stages from the stage field's selection.
        """
        # return [stages[0] for stages in self._fields["stage"].selection]
        return [key for key, label in self._fields['stage'].selection]

    def action_view_batches(self):
        """
        Open the call batch for the campaign in kanban, tree,
        and form views with a filtered domain.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_call.mis_call_batch_action_window"
        )
        action["display_name"] = _("%(name)s", name=self.name)
        action["view_mode"] = "kanban,tree,form"
        action["domain"] = [("campaign_id", "=", self.id)]
        action["context"] = {
            "default_campaign_id": self.id,
        }
        return action

    def _compute_assigned_call_count(self):
        """
        Dynamically compute the number of assigned calls for the current user.
        """
        for campaign in self:
            campaign.call_count = len(campaign.assigned_call_ids)


class MisCallCampaignTags(models.Model):
    _name = "mis.call.campaign.tags"
    _description = "MIS Call Campaign Tags"

    name = fields.Char(string="Tags")
    color = fields.Char(string="color")
