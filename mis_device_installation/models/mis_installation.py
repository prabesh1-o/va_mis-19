import json
from datetime import datetime, timedelta

from lxml import etree
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class MisDeviceInstallation(models.Model):
    _name = "mis.device.installation"
    _description = "Mis Device Installation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    def _get_default_stage_id(self):
        return (
            self.env["mis.device.installation.stage"].search([("sequence", "=", 0)]).id
        )

    name = fields.Char(compute="_compute_installation_name", store=True)
    customer_id = fields.Many2one(
        "res.partner",
        string="Client",
        domain='[("parent_id","=", None)]',
        required=True,
    )
    installation_line_ids = fields.One2many(
        "mis.device.installation.line", "installation_id", string="Installation Lines"
    )
    stage_id = fields.Many2one(
        "mis.device.installation.stage",
        string="Stage",
        store=True,
        readonly=False,
        default=_get_default_stage_id,
        group_expand="_read_group_stage_ids",
        ondelete="restrict",
        copy=False,
        tracking=True,
    )
    completed_stage_start_date = fields.Datetime()
    active = fields.Boolean(default=True)
    employee_ids = fields.Many2many("hr.employee", string="Assignee", tracking=True)
    tag_ids = fields.Many2many(
        "mis.device.installation.tags", string="Tags", tracking=True
    )
    is_repaired = fields.Boolean(default=False)
    is_relocation = fields.Boolean(string="Relocation")
    completeness = fields.Float("Completeness", readonly=True)
    date_deadline = fields.Date("Deadline")
    total_installations = fields.Integer(compute="_compute_total_numbers")
    total_installed_devices = fields.Integer(compute="_compute_total_numbers")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    total_installation_price = fields.Monetary(
        currency_field="company_currency_id",
        string="Installation Price",
        group_operator="sum",
        compute="_compute_installation_price",
        store=True,
    )
    total_neutral_devices = fields.Integer(compute="_compute_total_numbers")
    total_canceled_devices = fields.Integer(compute="_compute_total_numbers")
    installation_address = fields.Char(string="Installation Address")
    contact_person_name = fields.Char(string="Contact Name")
    contact_person_phone = fields.Char(string="Phone No.")

    def action_auto_fill_contact_details(self):
        for installation in self:
            for line in installation.installation_line_ids:
                line.installation_address = installation.installation_address
                line.contact_person_name = installation.contact_person_name
                line.contact_person_phone = installation.contact_person_phone
                line.employee_ids = installation.employee_ids

    @api.depends("installation_line_ids")
    def _compute_total_numbers(self):
        for installation in self:
            installation_lines = installation.installation_line_ids
            if installation_lines:
                installation.total_installations = len(installation_lines)
                installation.total_installed_devices = len(
                    installation_lines.filtered(lambda line: line.state == "installed")
                )
                installation.total_neutral_devices = len(
                    installation_lines.filtered(lambda line: line.state is False)
                )
                installation.total_canceled_devices = len(
                    installation_lines.filtered(lambda line: line.state == "canceled")
                )
            else:
                installation.total_installations = 0
                installation.total_installed_devices = 0
                installation.total_neutral_devices = 0
                installation.total_canceled_devices = 0

    def _get_completion(self):
        """Return the percentage of completeness of the goal, between 0 and 100"""
        for installation in self:
            line = self.installation_line_ids
            devices_installed = len(
                line.filtered(lambda line: line.state == "installed")
            )
            installation.completeness = (
                devices_installed / installation.total_installations
            ) * 100

    def update_inactive_installations(self):
        """
        Deactivates installations that have been in a completed stage for a
        specified number of days. The method retrieves the number of days from
        the configuration parameter `mis.mis_installation_completion_days_count`
        and calculates a date limit by subtracting this number of days from the
        current date and time. It then searches for installation records where the
        `stage_id` is marked as completed, the `completed_stage_start_date` is
        earlier than the calculated date limit, and the `active` status is
        currently `True`. If any installations meet these criteria, the method
        updates their `active` status to `False`, thereby deactivating them.
        """
        days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mis.mis_installation_completion_days_count")
        )
        date_limit = fields.Datetime.to_string(
            datetime.now() - timedelta(days=days_count)
        )
        renewals = self.search(
            [
                ("stage_id.is_complete_stage", "=", True),
                ("completed_stage_start_date", "<", date_limit),
                ("active", "=", True),
            ]
        )
        if renewals:
            renewals.write({"active": False})

    @api.depends("installation_line_ids", "installation_line_ids.installation_price")
    def _compute_installation_price(self):
        for installation in self:
            installation.total_installation_price = sum(
                line.installation_price for line in installation.installation_line_ids
            )

    @api.model
    def _read_group_stage_ids(self, stages, domain=None, order=None):
        stage_ids = stages._search(domain or [], order=order)
        return stages.browse(stage_ids)

    @api.depends("customer_id")
    @api.onchange("customer_id")
    def _compute_installation_name(self):
        for installation in self:
            if installation.customer_id:
                installation.name = f"Installation-{datetime.now().date()}-{installation.customer_id.name}"
            else:
                installation.name = ""

    def _onchange_stage(self):
        for order in self:
            order.installation_line_ids.write({"state": "progress"})

    @api.onchange("installation_line_ids.state")
    def _confirm_card_stage(self):
        verification_stage_id = self.stage_id.search(
            [("is_verification_stage", "=", True)]
        ).id
        for installation in self:
            if all(
                installation.installation_line_ids.mapped(
                    lambda line: line.state == "installed"
                )
            ):
                installation.stage_id = verification_stage_id
            self._get_completion()

    def _activate_customer(self):
        self.customer_id.is_customer = True

    def btn_configure_customer_and_devices(self):
        for installation in self:
            installed_devices_line = installation.installation_line_ids.filtered(
                lambda r: r.state == "installed"
            )
            if installed_devices_line:
                self._activate_customer()

    def _schedule_activities(self, vals):
        """
        Schedule activities for newly assigned employees in an installation.

        Args:
            vals (dict): Contains updates for an existing installation.
        """
        for installation in self:
            employee_ids = [
                id
                for employee in vals.get("employee_ids", [])
                for id in employee[2]
                if id not in installation.employee_ids.ids
            ]
            summary = _(f"Installation {installation.name} has been assigned.")
            user_ids = self.env["hr.employee"].browse(employee_ids).user_id
            for user_id in user_ids:
                if user_id:
                    self.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=user_id.id,
                        summary=summary,
                    )

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """
        This method extends the standard get_view functionality by adding automatic readonly
        behavior to form fields based on the group.
        When a user belong to group group_able_to_read_installation_and_sent_attachment,
        all editable fields will become readonly, implementing a common workflow pattern
        where users with read only access can send message and set activities.
        """
        res = super().get_view(view_id=view_id, view_type=view_type, **options,)
        if view_type == "form" and self.env.user.has_group(
            "mis_device_installation.group_able_to_read_installation_and_sent_attachment"
        ):
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name][not(ancestor::field)]"):
                modifiers = json.loads(
                    field.attrib.get("modifiers", '{"readonly": false}')
                )
                modifiers["readonly"] = True
                field.attrib["modifiers"] = json.dumps(modifiers)
            res["arch"] = etree.tostring(doc, pretty_print=True)
        return res

    def write(self, vals):
        for installation in self:
            if "employee_ids" in vals:
                self._schedule_activities(vals)
            if "stage_id" in vals:
                new_stage = self.env["mis.device.installation.stage"].browse(
                    vals["stage_id"]
                )
                if new_stage.is_complete_stage:
                    vals["completed_stage_start_date"] = fields.Datetime.now()
                if new_stage.is_in_progress_stage:
                    self._onchange_stage()
        installation = super().write(vals)
        return installation


class MisDeviceInstallationStage(models.Model):
    _name = "mis.device.installation.stage"
    _description = "Mis Device Installation Stage"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=1)
    is_default_stage = fields.Boolean(default=False)
    is_verification_stage = fields.Boolean(default=False)
    is_complete_stage = fields.Boolean(default=False)
    is_in_progress_stage = fields.Boolean(default=False)
    is_canceled_stage = fields.Boolean(default=False)
    requirements = fields.Text("Requirements")


class MisDeviceInstallationLine(models.Model):
    _name = "mis.device.installation.line"
    _description = "Mis Device Installation Line"

    installation_id = fields.Many2one(
        "mis.device.installation", string="Installation", ondelete="cascade", copy=False
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    renewal_price = fields.Monetary(
        currency_field="company_currency_id", group_operator="sum",
    )
    installation_price = fields.Monetary(
        currency_field="company_currency_id", group_operator="sum",
    )
    installation_date = fields.Date(string="Installation Date")
    installation_address = fields.Char(string="Installation Address")
    contact_person_name = fields.Char(string="Name")
    contact_person_phone = fields.Char(string="Phone No.")
    is_installation_complete = fields.Boolean(default=False)
    state = fields.Selection(
        selection=[
            ("progress", "In Progress"),
            ("installed", "Installed"),
            ("canceled", "Canceled"),
        ],
        string="Status",
    )
    employee_ids = fields.Many2many("hr.employee", string="Assignee")
    canceled_reason = fields.Text()
    is_configured = fields.Boolean(default=False)
    expiry_date = fields.Date(string="Expiration Date")

    def _onchange_installation_state(self):
        for line in self:
            installation = line.installation_id
            if installation.create_date:
                if (
                    installation.stage_id.is_in_progress_stage
                    or installation.stage_id.sequence == 0
                ):
                    installation._confirm_card_stage()
                else:
                    raise UserError(
                        _(
                            "You can change installation status only in Request and In Progress Stages"
                        )
                    )

    def action_rainbow_man(self):
        return {
            "effect": {
                "fadeout": "fast",
                "message": "Congratulations, all devices are installed successfully!",
                "type": "rainbow_man",
            }
        }

    def btn_update_installation_state(self):
        for line in self:
            if line.state != "installed":
                line.installation_date = datetime.now().date()
                line.state = "installed"
            elif line.state == "installed":
                line.installation_date = None
                line.state = "progress"
            if (
                line.installation_id.total_installations
                == line.installation_id.total_installed_devices
            ):
                return self.action_rainbow_man()

    def write(self, vals):
        line = super().write(vals)
        if "state" in vals:
            self._onchange_installation_state()
        return line


class MisDeviceInstallationTags(models.Model):
    _name = "mis.device.installation.tags"
    _description = "Mis Device Installation Tags"

    name = fields.Char(string="Name", required=True)
    color = fields.Char(string="color")
