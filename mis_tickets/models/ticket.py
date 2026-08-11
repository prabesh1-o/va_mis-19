from datetime import date, datetime, timedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class MisTicket(models.Model):
    _name = "mis.ticket"
    _description = "MIS Tickets"
    _order = "create_date desc, priority desc"
    _rec_name = "ticket_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_stage_id(self):
        """Gives default stage_id"""
        ticket_menu_id = self.env.context.get("default_ticket_menu_id")
        if not ticket_menu_id:
            return False
        return self.stage_find(ticket_menu_id, [("fold", "=", False)])

    ticket_id = fields.Char(string="Ticket Id.")
    description = fields.Html(string="Description", tracking=True, sanitize=True)
    priority = fields.Selection(
        [("0", "Low"), ("3", "Average"), ("9", "High")],
        default="0",
        string="Priority",
        required=True,
        tracking=True,
    )
    stage_id = fields.Many2one(
        "mis.ticket.stage",
        string="Stage",
        compute="_compute_stage_id",
        store=True,
        readonly=False,
        ondelete="restrict",
        domain="[('ticket_menu_ids', '=', ticket_menu_id)]",
        default=_get_default_stage_id,
        group_expand="_read_group_stage_ids",
        copy=False,
        tracking=True,
    )
    completed_stage_start_date = fields.Datetime()
    color = fields.Integer(
        "Color Index", default=0, help="Used to decorate kanban view"
    )
    issue_reporter = fields.Char(string="Issue Reporter(Name,Contact No.)")
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Assigneee",
        tracking=True,
        default=lambda self: self.env.user.employee_id,
    )
    ticket_menu_id = fields.Many2one(
        "mis.ticket.menu", ondelete="cascade", tracking=True
    )
    kanban_state = fields.Selection(
        [("normal", "In Progress"), ("done", "Ready"), ("blocked", "Need Assistance")],
        string="Status",
        copy=False,
        default="normal",
        required=True,
        compute="_compute_kanban_state",
        readonly=False,
        store=True,
        tracking=True,
    )
    tag_ids = fields.Many2many("mis.ticket.tags", string="Tags", tracking=True)
    customer_id = fields.Many2one("res.partner", string="Customer", tracking=True,)
    device_imei = fields.Char(string="Device")

    @api.model
    def hide_completed_tickets(self):
        """
        Hides completed tickets by moving them to a specific menu and stage based on configuration parameter.

        Retrieves the number of days from configuration parameter `mis.mis_tickets_completions_days_count`.
        Calculates the date limit by subtracting the retrieved number of days from the current date and time.
        Obtains the active ID from the current context. Fetches tickets that match the criteria using the
        `get_tickets_from_active_id` method with the calculated date limit and active ID.
        Searches for the menu and stage records where `is_completed` is set to `True`.
        If matching tickets and a completed menu are found,
        updates the tickets to move them to the completed menu and stage.
        """
        days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mis.mis_tickets_completions_days_count")
        )
        date_limit = fields.Datetime.to_string(
            datetime.now() - timedelta(days=days_count)
        )
        active_id = self.env.context.get("active_id")
        tickets = self.get_tickets_from_active_id(date_limit, active_id)
        completed_menu_id = (
            self.env["mis.ticket.menu"]
            .with_context(active_test=False)
            .search([("is_completed", "=", True)], limit=1)
        )
        completed_stage_id = self.env["mis.ticket.stage"].search(
            [("is_completed", "=", True)], limit=1
        )
        if tickets and completed_menu_id:
            tickets.write(
                {
                    "ticket_menu_id": completed_menu_id.id,
                    "stage_id": completed_stage_id.id,
                }
            )

    def get_tickets_from_active_id(self, date_limit, active_id):
        """
        Retrieves tickets based on the provided active ID and date limit.

        This method performs the following steps:
        1. If an `active_id` is provided:
        Fetches the `mis.ticket.menu` record corresponding to the `active_id`.
        Searches for tickets that match the following criteria:
            - Belong to the `ticket_menu_id` of the fetched menu record.
            - Have a stage where `is_completed` is set to `True`.
            - Have a `completed_stage_start_date` earlier than the specified `date_limit`.
        2. If no `active_id` is provided:
        Searches for tickets that match the following criteria:
            - Have a stage where `is_completed` is set to `True`.
            - Have a `completed_stage_start_date` earlier than the specified `date_limit`.
        """
        if active_id:
            ticket_menu = self.env["mis.ticket.menu"].browse(active_id)
            tickets = self.search(
                [
                    ("ticket_menu_id", "=", ticket_menu.id),
                    ("stage_id.is_completed", "=", True),
                    ("completed_stage_start_date", "<", date_limit),
                ]
            )
        else:
            tickets = self.search(
                [
                    ("stage_id.is_completed", "=", True),
                    ("completed_stage_start_date", "<", date_limit),
                ]
            )
        return tickets

    def stage_find(self, section_id, domain=[], order="sequence, id"):
        """Override of the base.stage method
        Parameter of the stage search taken from the lead:
        - section_id: if set, stages must belong to this section or
          be a default stage; if not set, stages must be default
          stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped("ticket_menu_id").ids)
        search_domain = []
        if section_ids:
            search_domain = ["|"] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(("ticket_menu_ids", "=", section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return (
            self.env["mis.ticket.stage"].search(search_domain, order=order, limit=1).id
        )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        search_domain = [("id", "in", stages.ids)]

        if "default_ticket_menu_id" in self.env.context:
            search_domain = [
                "|",
                ("ticket_menu_ids", "=", self.env.context["default_ticket_menu_id"]),
            ] + search_domain

        return stages.sudo().search(
        search_domain,
        order="sequence, id"
    )

    @api.depends("ticket_menu_id")
    def _compute_stage_id(self):
        for ticket in self:
            if ticket.ticket_menu_id:
                if ticket.ticket_menu_id not in ticket.stage_id.ticket_menu_ids:
                    ticket.stage_id = ticket.stage_find(
                        ticket.ticket_menu_id.id, [("fold", "=", False)]
                    )
            else:
                ticket.stage_id = False

    @api.onchange("priority")
    def _onchange_priority(self):
        for rec in self:
            if rec.priority:
                rec.color = int(rec.priority)

    def _generate_ticket_id(self, ticket_menu_name):
        if ticket_menu_name:
            recent_ticket = self.search([], order="id desc", limit=1, offset=1)
            if recent_ticket and (self._is_todays_ticket(recent_ticket)):
                recent_ticket_id = recent_ticket.ticket_id
                ticket_parts = recent_ticket_id.split("-")
                ticket_parts[0] = "".join(
                    word[0] for word in ticket_menu_name.split()
                ).upper()
                ticket_parts[-1] = str(int(ticket_parts[-1]) + 1)
                ticket_id = "-".join(ticket_parts)
                return ticket_id
            else:
                return self._create_new_ticket_id(ticket_menu_name)

    def _is_todays_ticket(self, ticket):
        return ticket.create_date.date() == date.today()

    def _create_new_ticket_id(self, ticket_menu_name):
        if ticket_menu_name:
            ticket_type_initials = "".join(
                word[0] for word in ticket_menu_name.split()
            ).upper()
            current_date = datetime.now().strftime("-%y-%m-%d")
            return f"{ticket_type_initials}{current_date}-1"

    @api.depends("stage_id", "ticket_menu_id")
    def _compute_kanban_state(self):
        self.kanban_state = "normal"

    def action_assign_to_me(self):
        for ticket in self:
            ticket.employee_ids = self.env.user.employee_id

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        for ticket in tickets:
            ticket.ticket_id = self._generate_ticket_id(ticket.ticket_menu_id.name)
        return tickets

    def _create_assignment_notification(self, vals):
        employee_ids = [
            id
            for employee in vals.get("employee_ids", [])
            for id in employee[2]
            if id not in self.employee_ids.ids
        ]
        recipient = self.env["hr.employee"].browse(employee_ids).user_id
        if recipient:
            for user in recipient:
                notification_ids = [
                    (
                        0,
                        0,
                        {
                            "res_partner_id": user.partner_id.id,
                            "notification_type": "inbox",
                        },
                    )
                ]
                self.env["mail.message"].create(
                    {
                        "message_type": "notification",
                        "body": f"{self.env.user.partner_id.name} assigned {user.partner_id.name}\
                                    a Ticket with Ticket id {self.ticket_id}",
                        "subject": "Ticket Assignment",
                        "partner_ids": [(4, user.partner_id.id)],
                        "model": self._name,
                        "res_id": self.id,
                        "notification_ids": notification_ids,
                        "author_id": self.env.user.partner_id
                        and self.env.user.partner_id.id,
                    }
                )
                user.notify_info(
                    message=f"{self.env.user.partner_id.name} \
                        assigned you a Ticket with Ticket id {self.ticket_id}",
                    title="Ticket Assigned",
                )

    def _schedule_activities(self, vals):
        """
        Schedule activities for newly assigned employees in a ticket.

        Args:
            vals (dict): Contains updates for an existing ticket.
        """
        for ticket in self:
            employee_ids = [
                id
                for employee in vals.get("employee_ids", [])
                for id in employee[2]
                if id not in ticket.employee_ids.ids
            ]
            summary = _(f"Complain {ticket.ticket_id} has been assigned.")
            user_ids = self.env["hr.employee"].browse(employee_ids).user_id
            for user_id in user_ids:
                if user_id:
                    self.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=user_id.id,
                        summary=summary,
                    )

    def write(self, vals):
        for rec in self:
            if "employee_ids" in vals:
                self._create_assignment_notification(vals)
                self._schedule_activities(vals)
            if "stage_id" in vals:
                new_stage = self.env["mis.ticket.stage"].browse(vals["stage_id"])
                if new_stage.is_completed:
                    vals["completed_stage_start_date"] = fields.Datetime.now()
        ticket = super().write(vals)
        return ticket


class MisTicketStage(models.Model):
    _name = "mis.ticket.stage"
    _description = "Mis Tickets Stage"
    _order = "sequence, id"

    def _get_default_ticket_menu_ids(self):
        default_ticket_menu_id = self.env.context.get("default_ticket_menu_id")
        return [default_ticket_menu_id] if default_ticket_menu_id else None

    name = fields.Char(string="Name", required=True, translate=True)
    is_completed = fields.Boolean(default=False)
    active = fields.Boolean(default=True)
    ticket_menu_ids = fields.Many2many(
        "mis.ticket.menu",
        "mis_ticket_menu_rel",
        "type_id",
        "ticket_menu_id",
        string="Ticket Menu",
        default=lambda self: self._get_default_ticket_menu_ids(),
    )
    fold = fields.Boolean(
        "Folded in Kanban",
        help="If enabled, this stage will be displayed as folded in \
            the Kanban view of your projects.\
            Projects in a folded stage are considered as closed.",
    )
    sequence = fields.Integer(default=1)
    requirements = fields.Text("Requirements")
    is_default_stage = fields.Boolean(default=False)

    @api.constrains("is_completed")
    def _check_is_completed(self):
        """
        Validates that only one stage can be marked as completed per ticket menu.

        This constraint method performs the following checks:
        Iterates over each record where the `is_completed` field is being set.
        If `is_completed` is `True` for a record it checks if there are other stages that
        are also marked as completed and are associated with the same ticket menus.
        Raises `ValidationError` if more than one stage is found to be completed for any ticket menu.
        """
        for record in self:
            if record.is_completed:
                for menu in record.ticket_menu_ids:
                    finished_stage = self.search(
                        [
                            ("is_completed", "=", True),
                            ("id", "!=", record.id),
                            ("ticket_menu_ids", "in", [menu.id]),
                        ]
                    )
                    if finished_stage:
                        raise ValidationError(
                            _(
                                "Only one stage can be marked as finished per ticket menu."
                            )
                        )


class MisTicketTags(models.Model):
    _name = "mis.ticket.tags"
    _description = "Mis Tickets Type"

    name = fields.Char(string="Name")
    color = fields.Char(string="color")
    ticket_menu_ids = fields.Many2many("mis.ticket.menu", string="Ticket Menu")
    ticket_ids = fields.Many2many("mis.ticket", string="Ticket")
    _sql_constraints = [
        ("name_uniq", "unique (name)", "A tag with the same name already exists."),
    ]
