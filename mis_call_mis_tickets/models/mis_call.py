from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisCall(models.Model):
    _inherit = "mis.call"

    ticket_ids = fields.One2many("mis.ticket", "call_id", string="Ticket")
    ticket_menu_id = fields.Many2one("mis.ticket.menu", string="Ticket Menu")
    category = fields.Selection(
        selection_add=[("ticket", "Ticket")], ondelete={"ticket": "set default",},
    )
    priority = fields.Selection(
        [("0", "Low"), ("3", "Average"), ("9", "High")],
        string="Priority",
        tracking=True,
    )
    ticket_tag_ids = fields.Many2many("mis.ticket.tags", string="Tags", tracking=True)
    has_ticket = fields.Boolean(compute="_compute_has_ticket")
    stage_id = fields.Many2one("mis.ticket.stage", string="Stage")

    @api.depends("ticket_tag_ids")
    def _compute_has_ticket(self):
        """
        Compute the value of the `has_ticket` field based on the `ticket_ids` field.

        This method iterates over each record in `self` and sets the `has_ticket`
        field to `True` if there is at least one ticket record in `ticket_ids`,
        and `False` otherwise.
        """
        for call in self:
            if call.ticket_ids:
                call.has_ticket = True
            else:
                call.has_ticket = False

    def action_create_ticket(self):
        """
        Creates a new ticket for the current record if it does not already have one.

        This method performs the following steps:
        1. Ensures the operation is performed on a single record.
        2. Finds the initial stage for the new ticket based on the current record's `ticket_menu_id`.
        - The stage is determined by searching the `mis.ticket.stage` model, ordered by sequence.
        3. Prepares the values required to create the new ticket.
        - Includes customer ID, vehicle ID, priority, tags, description,
            ticket menu ID, call ID, and stage ID.
        4. Creates the new ticket in the `mis.ticket` model with the prepared values.

        Raises:
            UserError: If the ticket already exists for the current record.
        """
        self.ensure_one()
        stage = self.env["mis.ticket.stage"].search(
            [("ticket_menu_ids", "=", self.ticket_menu_id.id)],
            order="sequence asc",
            limit=1,
        )
        ticket_vals = {
            "customer_id": self.customer_id.id,
            "vehicle_id": self.vehicle_id.id,
            "priority": self.priority,
            "tag_ids": self.ticket_tag_ids,
            "employee_ids": self.user_id,
            "description": self.description,
            "ticket_menu_id": self.ticket_menu_id.id,
            "call_id": self.id,
            "stage_id": stage.id,
            "issue_reporter": f"{self.number} - {self.reporter}",
        }
        self.env["mis.ticket"].create(ticket_vals)

    def action_view_ticket(self):
        """
        Open the form view of the associated ticket record.

        This method retrieves the action to open the form view of the associated
        ticket record. If a ticket record exists for the current call record,
        it sets the `res_id` of the action to the ID of the ticket record and
        filters the views to show only the form view.

        Returns:
            dict: The action to open the form view of the associated ticket record.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_tickets.action_view_all_ticket_views"
        )
        action["context"] = {"search_default_call_id": self.id}
        action["view_mode"] = "form"
        action["res_id"] = self.ticket_ids.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action

    @api.onchange("category")
    def _onchange_category(self):
        """
        Handle changes to the 'category' field.

        This method is triggered when there is a change in the 'category' field of the record.
        It checks whether certain other fields in the record are set. If any of the specified
        fields are already populated, it raises a ValidationError to prevent changing the category.

        Raises:
            ValidationError: If any of the following fields are set:
                - customer_id
                - ticket_menu_id
                - vehicle_id
                - ticket_tag_ids
                - priority
                - description
            The error message instructs the user that they cannot change the category and
            suggests discarding the changes or creating a new call record.
        """
        fields_to_check = [
            self.ticket_menu_id,
            self.vehicle_id,
            self.customer_id,
            self.ticket_tag_ids,
            self.priority,
            self.user_id,
            self.description,
        ]
        if any(fields_to_check):
            raise ValidationError(
                _(
                    "You cannot change the category now. \nDiscard the changes or create a new call record."
                )
            )
