from odoo import _, api, fields, models


class MisCallBatch(models.Model):
    _name = "mis.call.batch"
    _description = "MIS Call Batch"

    name = fields.Char(string="ID", readonly=True)
    description = fields.Char(string="Description")
    campaign_id = fields.Many2one("mis.call.campaign", string="Campaign")
    assigned_by = fields.Many2one(
        "hr.employee",
        string="Assigned By",
        default=lambda self: self.env.user.employee_id,
    )
    assigned_call_ids = fields.One2many(
        "mis.assign.call", "batch_id", string="Assigned Calls"
    )
    call_count = fields.Integer(
        compute="_compute_assigned_call_count", string="Call Count", store=False
    )

    def _compute_assigned_call_count(self):
        """
        Dynamically compute the number of assigned calls for the current user.
        """
        for batch in self:
            batch.call_count = len(batch.assigned_call_ids)

    def action_view_assigned_calls(self):
        """
        Open the assigned calls for the campaign in tree, kanban,
        and form views with a filtered domain.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_call.mis_assigned_call_menu_action_window"
        )
        action["display_name"] = _(f"{self.name}s")
        action["view_mode"] = "tree,kanban,form"
        action["domain"] = [("batch_id", "=", self.id)]
        action["context"] = {
            "default_batch_id": self.id,
        }
        return action

    def _generate_batch_name(self):
        """
        Generates a unique batch name based on the most recent batch for the same campaign.
        The batch name is formed by appending a numeric part to the first four characters
        of the most recent batch name. If no recent batch exists, the batch name is
        generated using the campaign's name and a starting numeric part.

        Returns:
            str: The generated batch name.
        """
        recent_batch = self.search(
            [("campaign_id", "=", self.campaign_id.id)],
            order="id desc",
            limit=1,
            offset=1,
        )
        if recent_batch:
            recent_batch_name = recent_batch.name
            numeric_part = int(recent_batch_name[4:]) + 1
            new_batch = recent_batch_name[:4] + str(numeric_part).zfill(3)
            return new_batch
        else:
            return f"{self._extract_campaign_name()}-B{str(1).zfill(3)}"

    def _extract_campaign_name(self):
        """
        Extracts and returns the first two characters of the associated campaign's name,
        converted to uppercase.

        Returns:
            str: The first two uppercase characters of the campaign's name.
        """
        campaign_name = self.campaign_id.name
        return campaign_name[:2].upper()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the default create method to assign a generated batch name to each
        batch record in the provided list of values.

        Args:
            vals_list (list): A list of dictionaries containing values to create new batch records.

        Returns:
            recordset: The newly created batch records with assigned batch names.
        """
        batches = super().create(vals_list)
        for batch in batches:
            batch.name = batch._generate_batch_name()
        return batches
