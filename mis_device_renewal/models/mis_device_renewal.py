from datetime import datetime, timedelta

from odoo import SUPERUSER_ID, Command, _, api, fields, models
from odoo.exceptions import UserError


class MisDeviceRenewal(models.Model):
    _name = "mis.device.renewal"
    _description = "MIS Renewal"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc, id desc"

    def _get_default_stage_id(self):
        return self.env["mis.device.renewal.stage"].search([("sequence", "=", 0)]).id

    def _get_default_grace_period(self):
        return (
            self.env["mis.device.renewal.grace.period"]
            .search([("is_default", "=", True)])
            .id
            or None
        )

    name = fields.Char(string="Name", compute="_compute_renewal_name", store=True)
    stage_id = fields.Many2one(
        "mis.device.renewal.stage",
        string="Stage",
        store=True,
        readonly=False,
        default=_get_default_stage_id,
        group_expand="_read_group_stage_ids",
        ondelete="restrict",
        copy=False,
        tracking=True,
    )
    device_ids = fields.Many2many(
        "mis.device", "device_customer_renewal_rels", tracking=True,
    )

    # Field to make the exp_expiration_date(store=True) always compute
    # when expiration type is automatic
    is_expiry_trigger = fields.Boolean(compute="_compute_expiry_trigger")
    customer_ids = fields.Many2many(
        "res.partner", domain="[('is_customer', '=', True)]", tracking=True,
    )
    employee_ids = fields.Many2many("hr.employee", string="Assignee", tracking=True)
    renewal_device_count = fields.Integer(compute="_compute_renewal_device_count")
    company_currency_id = fields.Many2one(related="device_ids.company_currency_id")
    total_renewal_amount = fields.Monetary(
        compute="_compute_amount",
        currency_field="company_currency_id",
        group_operator="sum",
        string="Total Renewal Amount",
        store=True,
    )
    total_untaxed_amount = fields.Monetary(
        compute="_compute_amount",
        string="Untaxed amount",
        currency_field="company_currency_id",
        readonly=True,
        store=True,
    )
    tax_amount = fields.Monetary(
        compute="_compute_amount",
        string="Taxes",
        currency_field="company_currency_id",
        readonly=True,
        store=True,
    )
    tag_ids = fields.Many2many("mis.device.renewal.tags", string="Tags", tracking=True)
    completed_stage_start_date = fields.Datetime()
    active = fields.Boolean(default=True)
    renewal_ticket_count = fields.Integer(
        string="Count",
        compute="_compute_renewal_ticket_count",
        help="Renewal Ticket Count of Same Customer on the pipeline",
    )
    grace_period_start = fields.Date(string="Grace Period Start", tracking=True)
    grace_period_end = fields.Date(string="Grace Period End", tracking=True)
    grace_period_days_count = fields.Integer(string="Grace Period Days")
    is_renewal_history_created = fields.Boolean(default=False)
    invoice_ids = fields.One2many("account.move", "renewal_id", string="Invoice")
    invoice_count = fields.Integer(compute="_compute_invoice_count", string="Invoices")
    grace_period_count = fields.Integer(
        compute="_compute_grace_period_count", string="Grace Period Count"
    )
    total_time_grace_period = fields.Integer()
    grace_period_id = fields.Many2one(
        "mis.device.renewal.grace.period",
        string="Grace Period",
        default=_get_default_grace_period,
        tracking=True,
    )

    def _compute_invoice_count(self):
        """
        Computes and updates the `invoice_count` for each renewal.

        - Sets the count based on the number of records in `invoice_ids`.
        """
        for renewal in self:
            renewal.invoice_count = len(renewal.invoice_ids)

    def update_stage_grace_period_renewal_card(self):
        """
        Update grace period renewal cards and move eligible devices to the
        stage with sequence 1 (Idle).
        """
        grace_period_cards = self.search(
            [("stage_id.is_grace_period_stage", "=", True)]
        )
        idle_stage = self.env["mis.device.renewal.stage"].search(
            [("sequence", "=", 1)], limit=1
        )
        for card in grace_period_cards:
            self._process_grace_period_card(card, idle_stage)

    def _process_grace_period_card(self, card, idle_stage):
        """
        Processes the grace period for devices in a given card and moves them to the
        idle stage if they exceed their grace period.

        - Identifies devices in the card that have exceeded their grace period.
        - Moves devices to the idle stage if only some devices have exceeded their grace period.
        - Sets the card's stage to the idle stage if all devices have exceeded their grace period.
        """
        today = datetime.now().date()
        devices_to_be_idle = [
            device.id
            for device in card.device_ids
            if device.grace_period_count >= device.grace_period_id.period_duration
        ]
        if len(devices_to_be_idle) != 0:
            if len(devices_to_be_idle) != len(card.device_ids):
                self._move_devices_to_idle(card, idle_stage, devices_to_be_idle, today)
            else:
                card.stage_id = idle_stage.id

    def _move_devices_to_idle(self, card, idle_stage, devices_to_be_idle, today):
        """
        Moves devices that have exceeded their grace period to the idle stage and creates a
        new renewal record.

        - Creates a new renewal record with the idle stage and associated devices.
        - Updates the devices' `grace_period_end` date and recalculates their grace period.
        - Removes the moved devices from the current card.

        Returns:
            new_renewal (Record): The newly created renewal record with devices moved to idle.
        """
        new_renewal = self.env["mis.device.renewal"].create(
            {
                "stage_id": idle_stage.id,
                "customer_ids": [(6, 0, card.customer_ids.ids)],
                "employee_ids": [(6, 0, card.employee_ids.ids)],
                "tag_ids": [(6, 0, card.tag_ids.ids)],
                "device_ids": [(6, 0, devices_to_be_idle)],
            }
        )
        devices = self.env["mis.device"].browse(devices_to_be_idle)
        devices.write({"grace_period_end": today})
        self._compute_grace_period_days_count(devices)
        card.write({"device_ids": [(3, device_id) for device_id in devices_to_be_idle]})
        return new_renewal

    def _compute_expiry_trigger(self):
        """
        Triggers the expiration date computation for devices in a renewal.

        - Sets the `is_expiry_trigger` flag to True for each renewal.
        - Checks if the renewal stage is eligible (with sequence 0, 1, or 2).
        - If eligible, it calls the `compute_expiry_date` method for devices with an
          "automatic" expiry date type.
        """
        for renewal in self:
            renewal.is_expiry_trigger = True
            stages = (
                self.env["mis.device.renewal.stage"]
                .search([("sequence", "in", [0, 1, 2])])
                .ids
            )
            if renewal.stage_id.id in stages:
                for device in renewal.device_ids:
                    if device.expiry_date_type == "automatic":
                        device.compute_expiry_date()

    @api.depends("customer_ids")
    def _compute_renewal_name(self):
        """
        Computes and updates the `name` for each renewal based on its ID.

        - The `name` is set to "R" followed by the renewal's ID, padded to 4 digits.
        """
        for renewal in self:
            renewal.name = f"R{str(renewal.id).zfill(4)}"

    @api.depends("grace_period_start", "grace_period_end")
    def _compute_grace_period_count(self):
        """
        Computes and updates the `grace_period_count` for each renewal based on
        the grace period start and the expiration status of devices.

        - If any device has expired and a grace period start is defined, it calculates
        the number of days from the grace period start to the current date.
        - If no devices are expired or grace period start is not set, the count is set to 0.
        """
        for renewal in self:
            is_any_device_expired = any(
                [
                    True if device.expiration_time else False
                    for device in renewal.device_ids
                ]
            )
            if renewal.grace_period_start and is_any_device_expired:
                renewal.grace_period_count = (
                    datetime.now().date() - renewal.grace_period_start
                ).days
            else:
                renewal.grace_period_count = 0

    def _compute_renewal_ticket_count(self):
        """
        Computes and updates the `renewal_ticket_count` for each renewal based on
        the number of tickets associated with the customer.

        - Counts the number of renewals that are linked to the same customer(s).
        """
        for renewal in self:
            renewal.renewal_ticket_count = self.search_count(
                [("customer_ids", "in", renewal.customer_ids.ids)]
            )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """
        Retrieves and returns the stages based on the specified order, ignoring any
        domain filters.

        - Searches for stage IDs with the provided order.
        - Returns the stages corresponding to the found stage IDs.

        Returns:
            Recordset: The stages matching the retrieved stage IDs.
        """
        return stages.sudo().search([])

    @api.depends(
        "device_ids",
        "device_ids.tax_amount",
        "device_ids.price_subtotal",
        "device_ids.renewal_price",
    )
    def _compute_amount(self):
        """
        Computes and updates the total amounts for each renewal based on its associated devices.

        - `total_renewal_amount`: The sum of the `price_subtotal` of all devices in the renewal.
        - `total_untaxed_amount`: The sum of the `current_renewal_price` of all devices in the renewal.
        - `tax_amount`: The sum of the `tax_amount` of all devices in the renewal.
        """
        for renewal in self:
            renewal.total_renewal_amount = sum(
                renewal.device_ids.mapped("price_subtotal")
            )
            renewal.total_untaxed_amount = sum(
                renewal.device_ids.mapped("current_renewal_price")
            )
            renewal.tax_amount = sum(renewal.device_ids.mapped("tax_amount"))

    @api.depends("device_ids")
    def _compute_renewal_device_count(self):
        """
        Computes and updates the `renewal_device_count` for each renewal based on the number of devices.

        - Sets the `renewal_device_count` to the number of devices associated with the renewal.
        """
        for renewal in self:
            renewal.renewal_device_count = len(renewal.device_ids)

    def btn_create_invoice(self):
        """
        Creates an invoice for the renewal if certain conditions are met.

        - Checks if an invoice has already been created and raises an error if true.
        - Validates that all devices associated with the renewal have tax information.
        - Ensures that the renewal is not in the "Open Stage" before allowing the creation of an invoice.
        - If valid, creates the invoice for the renewal with the corresponding customer and invoice lines.

        Raises:
            - UserError: If an invoice is already created, if any device is missing tax,
              or if the renewal is in the "Open Stage".
        """
        for renewal in self:
            if renewal.invoice_ids:
                raise UserError(_("Invoice is already created"))
            self._validate_device_service()
            if renewal.device_ids.filtered(lambda d: not d.tax_id):
                raise UserError(_("Every line must have tax to create invoice"))
            if renewal.stage_id.sequence != 0:
                self.write(
                    {
                        "invoice_ids": [
                            (
                                0,
                                0,
                                {
                                    "partner_id": renewal.customer_ids.id,
                                    "move_type": "out_invoice",
                                    "invoice_line_ids": renewal._prepare_invoice_lines(),
                                },
                            )
                        ]
                    }
                )
            else:
                raise UserError(_("Sorry, You cannot create invoice in Open Stage"))

    def _prepare_invoice_lines(self):
        """
        Prepares the invoice lines for the renewal, grouping devices by their service and price.

        - For each service, it filters the devices associated with that service, counts the occurrences
        of each price, and prepares invoice lines with the service name, quantity, and unit price.
        - Returns a list of tuples containing the necessary information for creating the invoice lines.

        Returns:
            list: A list of tuples representing the invoice lines to be created.
        """
        self.ensure_one()
        invoice_lines = []
        for service in self.device_ids.service_id:
            devices = self.device_ids.filtered(lambda rec: rec.service_id == service)
            prices = devices.mapped("current_renewal_price")
            prices_count = {price: prices.count(price) for price in prices}
            invoice_lines.extend(
                [
                    (
                        0,
                        0,
                        {
                            "name": f"Renewal({service.name})",
                            "quantity": count,
                            "price_unit": price,
                        },
                    )
                    for price, count in prices_count.items()
                ]
            )
        return invoice_lines

    def action_view_renewal(self):
        """
        Displays the invoice(s) related to the renewal.

        - If there is exactly one invoice linked to the renewal, it opens the invoice in form view.
        - If multiple invoices exist, it shows the list of invoices.
        - Sets the domain to filter invoices related to the current renewal.

        Returns:
            dict: The action to display the related invoices.
        """
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        action["domain"] = [("renewal_id", "=", self.id)]
        if self.invoice_count == 1:
            action["view_mode"] = "form"
            action["res_id"] = self.invoice_ids.id
            if "views" in action:
                action["views"] = [
                    (view_id, view_type)
                    for view_id, view_type in action["views"]
                    if view_type == "form"
                ]
        return action

    def update_inactive_renewals(self):
        """
        Deactivates renewals that have been in a completed stage for
         a specified number of days. The method first retrieves the
        number of days from the configuration parameter
        `mis.mis_renewal_completion_days_count` and calculates a date
        limit by subtracting this number from the current date and time.
        It then searches for renewal records where the `stage_id` is marked
        as completed, the `completed_stage_start_date` is earlier than the
        calculated date limit, and the `active` status is currently `True`.
        If any renewals meet these criteria, the method updates their
        `active` status to `False`, effectively deactivating them.
        """
        days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mis.mis_renewal_completion_days_count")
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

    def update_expired_device_list(self):
        """
        Updates the list of expired devices and associates them with renewal tickets if needed.

        - Searches for devices that are expired or will expire soon based on the configured days count.
        - Filters out devices that are already linked to existing renewal tickets.
        - For each new expired device, checks if a renewal ticket with the customer exists in the open stage.
        - If not, creates a new renewal ticket and associates the expired device.
        - Sends a renewal message for newly added expired devices.
        """
        today = datetime.now().date()
        days_count = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mis.mis_renewal_expiry_days_count")
        )
        expired_devices = self.env["mis.device"].search(
            [
                ("expiration_time", ">", today),
                ("expiration_time", "<=", today + timedelta(days=days_count)),
                ("customer_id.is_blacklist", "=", False),
            ]
        )
        already_existing_devices = self.search([]).device_ids.ids
        new_devices = expired_devices.filtered(
            lambda record: record.id not in already_existing_devices
        )
        for device in new_devices:
            renewal_tickets_in_open_stage = self.search([("stage_id.sequence", "=", 0)])
            tickets_with_multiple_customer = [
                ticket.customer_ids
                for ticket in renewal_tickets_in_open_stage
                if len(ticket.customer_ids) > 1
            ]
            customers = device.customer_id
            if (
                customers
                and customers not in renewal_tickets_in_open_stage.customer_ids
            ):
                if customers not in tickets_with_multiple_customer:
                    self.with_context(scheduler=True).create(
                        {"customer_ids": [(4, customer.id) for customer in customers]}
                    )
            if renewal_tickets_in_open_stage:
                self._add_expired_devices_in_renewal_ticket(device)
        self._create_renewal_message(new_devices)

    def _add_expired_devices_in_renewal_ticket(self, device):
        """
        Adds expired devices to the appropriate renewal ticket based on the customer.

        - Searches for renewal tickets in the "Open Stage" (sequence = 0).
        - If a renewal ticket exists for the device's customer, the expired device is
          added to the renewal ticket.

        Args:
            device: The expired device to be added to the renewal ticket.
        """
        renewals = self.search([("stage_id.sequence", "=", 0)])
        for renewal in renewals:
            if renewal.customer_ids in device.customer_id:
                renewal.write({"device_ids": [(4, device.id)]})

    def action_pi_send(self):
        """
        Opens a wizard to compose an email, with renewal PI mail template loaded by default.

        Returns:
            dict: An action dictionary to open the mail.compose.message form in a modal window,
            pre-filled with the appropriate email template and settings.
        """
        self.ensure_one()
        if self.stage_id.sequence == 5:
            raise UserError(
                _("Pro Forma Invoice cannot be sent in the Completed stage.")
            )
        if len(self.employee_ids) != 1:
            raise UserError(_("There should be only one assignee while sending PI."))
        mail_template = self.env.ref(
            "mis_device_renewal.email_template_pi_renewal", raise_if_not_found=False
        )
        ctx = {
            "default_model": "mis.device.renewal",
            "default_res_id": self.id,
            "default_use_template": bool(mail_template),
            "default_template_id": mail_template.id if mail_template else None,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    def _create_renewal_message(self, devices):
        """
        Generates an HTML message listing the devices that are expiring and sends it.

        - Creates an HTML table with the device's IMEI number, customer name(s), and phone number(s).
        - Calls `_send_renewal_message` to send the generated HTML message.

        Args:
            devices: A list of devices that are expiring.
        """
        html = """
        <h2 class="text-danger"><center>Expiring Devices</center></h2>
        <table class="table table-bordered table-responsive">
        <tr>
        <th scope="col">Devices</th>
        <th scope="col">Customer</th>
        <th scope="col">Phone no </th>
        """
        for device in devices:
            customers = device.customer_id
            customer_names = ",".join(customers.mapped("name"))
            numbers = customers.mapped("phone") + customers.mapped("mobile")
            phone_numbers = ", ".join([number for number in numbers if number])
            html += f"""
            <tr>
            <td>{device.imei_no}</td>
            <td>{customer_names}</td>
            <td>{phone_numbers}</td>
            </tr>
            """
        html += """</table>"""
        self._send_renewal_message(html)

    def _send_renewal_message(self, html):
        """
        Sends a renewal message with a list of expiring devices to the relevant partners.

        - Retrieves the list of partners who are authorized to read renewal information.
        - Sends an inbox notification with an HTML body containing the renewal details.

        Args:
            html (str): The HTML-formatted content to be sent in the message body.
        """
        odoobot_id = self.env["ir.model.data"]._xmlid_to_res_id("base.partner_root")
        partners = (
            self.env.ref(
                "mis_device_renewal.group_mis_device_renewal_all_documents"
            ).users.partner_id
            | self.env.ref(
                "mis_device_renewal.group_mis_device_renewal_administrator"
            ).users.partner_id
        )
        notification_ids = [
            (0, 0, {"res_partner_id": partner.id, "notification_type": "inbox"})
            for partner in partners
        ]
        self.env["mail.message"].create(
            {
                "message_type": "comment",
                "body": html,
                "subject": "Renewal List",
                "partner_ids": [(4, partner_id) for partner_id in partners.ids],
                "model": self._name,
                "notification_ids": notification_ids,
                "res_id": self.id,
                "author_id": odoobot_id,
            }
        )

    def create_renewal_history(self):
        """
        Creates a renewal history record for each device associated with the renewal.

        - Validates the device packages, payment status, and customer billing
          information before creating the history.
        - If the renewal is for a billed customer, payment validation is applied.
        - Creates or updates the renewal history for each device, including details
          such as old and new expiry dates, payment date, and renewal price.
        - Sets the `is_renewal_history_created` flag to True once history is successfully created.

        Raises:
            - UserError: If the device list for the renewal is empty.
        """
        for renewal in self:
            devices = renewal.device_ids
            is_billed_customer = (
                True if renewal.customer_ids.is_billed_customer else False
            )
            billed_renewed_stage = renewal.stage_id.is_billed_renewed_stage
            device_renewal_history = self.env["mis.device.renewal.history"]
            if devices:
                if billed_renewed_stage:
                    self._validate_billed_customer()
                else:
                    self._validate_device_payment(devices)
                for device in devices:
                    if device.renewal_package_id and device.renewal_price:
                        if not renewal.is_renewal_history_created:
                            device_renewal_history.create(
                                {
                                    "device_id": device.id,
                                    "old_expiry_date": device.expiration_time,
                                    "expiry_date": device.exp_expiration_date,
                                    "payment_date": device.payment_date,
                                    "renewal_id": renewal.id,
                                    "grace_period_days_count": device.grace_period_days_count,
                                    "renewal_price": device.current_renewal_price,
                                }
                            )
                        else:
                            if is_billed_customer:
                                self._validate_device_payment(device)
                                device_renewal_history.search(
                                    [("device_id", "in", self.device_ids.ids)],
                                    order="create_date desc",
                                    limit=1,
                                ).write({"payment_date": device.payment_date})
                renewal.is_renewal_history_created = True
            else:
                raise UserError(_("Renewal Device List Cannot Be Empty"))

    def _validate_device_payment(self, devices):
        """
        Validates that a payment date is set for each device in the provided list.

        - Raises an error if any device in the list does not have a payment date set.

        Args:
            devices: A list of devices to validate.

        Raises:
            - UserError: If any device does not have a payment date set.
        """
        for device in devices:
            if not device.payment_date:
                raise UserError(
                    _(
                        "Payment Date Is not Set, Please Set Required Payment Date And Proceed"
                    )
                )

    def _validate_idle_after_grace_stage(self, new_stage):
        """
        Validates that a stage after grace is idle.

        - Raises an error if the stage of renewal after grace is not idle.

        Args:
            new_stage: A new stage to which card is moved.

        Raises:
            - UserError: If the stage after grace is not idle.
        """
        for renewal in self:
            if new_stage.sequence != 1 and renewal.stage_id.is_grace_period_stage:
                raise UserError(
                    _(
                        "The renewal card should be moved to Idle"
                        " from Grace before proceeding further."
                    )
                )

    def _validate_device_package(self):
        """
        Validates that each device in the provided list has a renewal package and a renewal price.

        - Raises an error if any device is missing a renewal package or renewal price.

        Args:
            self: Objects of devices.

        Raises:
            - UserError: If any device does not have both a renewal package and renewal price set.
        """
        for renewal in self:
            for device in renewal.device_ids:
                if not (device.renewal_package_id and device.renewal_price):
                    raise UserError(
                        _(
                            "Every Device Must Contain Renewal Package and Respective Price"
                        )
                    )

    def _validate_billed_customer(self):
        """
        Validates that all customers associated with the renewal are billed customers.

        - Checks if each customer in the renewal is a billed customer.
        - Raises an error if any customer is not a billed customer.

        Raises:
            - UserError: If any customer is not marked as a billed customer.
        """
        for renewal in self:
            customers = renewal.customer_ids
            for customer in customers:
                if not customer.is_billed_customer:
                    raise UserError(_("The Customer Must be a Billed Customer"))

    def _validate_device_service(self):
        """
        Ensures that all devices in the renewal have an associated service.

        Raises:
            UserError: If any device is missing a service.
        """
        for renewal in self:
            for renewal in self:
                devices_without_service = renewal.device_ids.filtered(
                    lambda device: not device.service_id
                )
            if devices_without_service:
                raise UserError(_("Every Device Must Contain Service"))

    @api.onchange("device_ids")
    def _validate_manual_expiry_date_change(self):
        """
        Prevents manual expiration date changes for devices in stages beyond Open, Idle, and Grace Period.
        """
        for renewal in self:
            old_devices = renewal._origin.device_ids
            new_devices = renewal.device_ids
            for device in new_devices:
                old_device = old_devices.filtered(lambda d: d.imei_no == device.imei_no)
                if (
                    old_device
                    and device.expiry_date_type == "manual"
                    and old_device.exp_expiration_date != device.exp_expiration_date
                    and renewal.stage_id.sequence not in (0, 1, 2)
                ):
                    raise UserError(
                        _(
                            "Expiration date can be changed manually only"
                            " in Open, Idle and Grace Period stages"
                        )
                    )

    def _reset_device_grace_info(self):
        """
        Resets grace period and expiration-related fields for all devices in the renewal.
        """
        for renewal in self:
            devices = renewal.device_ids
            for device in devices:
                device.write(
                    {
                        "payment_date": None,
                        "grace_period_start": None,
                        "grace_period_end": None,
                        "grace_period_days_count": None,
                        "grace_period_count": None,
                        "total_time_grace_period": None,
                    }
                )

    def create_payment_date(self):
        """
        Sets the payment date for each device in the renewal.

        - Validates that each device has a renewal package.
        - Sets the payment date to the current date for devices in the renewal.
        - If the renewal history is already created, the payment date is only set for billed customers.

        Raises:
            - UserError: If the device list for the renewal is empty.
        """
        for renewal in self:
            devices = renewal.device_ids
            if devices:
                for device in devices:
                    if not self.is_renewal_history_created:
                        device.payment_date = datetime.now().date()
                    else:
                        if renewal.customer_ids.is_billed_customer:
                            device.payment_date = datetime.now().date()
            else:
                raise UserError(_("Renewal Device List Cannot Be Empty"))

    def _compute_grace_period_days_count(self, devices):
        """
        Computes and updates the grace period days count for each device in the list.

        For each device, if both `grace_period_start` and `grace_period_end` are defined,
        it calculates the number of grace days using the device's `compute_grace_days_count`
        method, adds the result to `grace_period_days_count`, and then resets the
        `grace_period_start` and `grace_period_end` to None.

        Args:
            devices (list): A list of device objects that have grace period attributes and
                            a `compute_grace_days_count` method.
        """
        for device in devices:
            if device.grace_period_start and device.grace_period_end:
                device.grace_period_days_count += device.compute_grace_days_count(
                    device.grace_period_end, device
                )
                device.grace_period_start = None
                device.grace_period_end = None

    def handle_grace_period_stage(self, grace_period_stage_id, new_stage_id):
        """
        Handles the transition of devices into or out of a grace period stage during a renewal process.

        For each renewal record:
        - If transitioning **into** the grace period stage (i.e., the new stage is the grace period and
        the current stage is not), sets the device's `grace_period_start` to today, clears
        `grace_period_end`, and increments `total_time_grace_period`.
        - If transitioning **out of** the grace period stage (i.e., the current stage is the grace period
        and the new stage is not), sets `grace_period_end` to today and computes the number of grace
        period days using `_compute_grace_period_days_count`.

        Args:
            grace_period_stage_id (int): The ID representing the grace period stage.
            new_stage_id (int): The ID representing the stage to which the record is transitioning.
        """
        today = datetime.now().date()
        for renewal in self:
            current_stage_id = renewal.stage_id.id
            for device in renewal.device_ids:
                if (
                    new_stage_id == grace_period_stage_id
                    and current_stage_id != grace_period_stage_id
                ):
                    device.grace_period_start = today
                    device.grace_period_end = None
                    device.total_time_grace_period += 1
                elif (
                    current_stage_id == grace_period_stage_id
                    and new_stage_id != grace_period_stage_id
                ):
                    device.grace_period_end = today
                    self._compute_grace_period_days_count(device)

    def _mail_track(self, tracked_fields, initial_values):
        """
        Tracks changes to the fields of the record, particularly Many2many and One2many fields.
        Specifically monitors the `device_ids` field for added or removed devices and posts a
        message about the change. Also prepares and stores the tracking values for the fields.

        Args:
            tracked_fields (dict): A dictionary of fields being tracked and their attributes.
            initial_values (dict): A dictionary of initial values for the fields before the change.

        Returns:
            tuple: A tuple containing the list of changes and the corresponding tracking value IDs.
        """
        changes, tracking_value_ids = super()._mail_track(
            tracked_fields, initial_values
        )
        # Many2many tracking
        if len(changes) > len(tracking_value_ids):
            for changed_field in changes:
                if tracked_fields[changed_field]["type"] in ["one2many", "many2many"]:
                    field = self.env["ir.model.fields"]._get(self._name, changed_field)
                    # post message if device has been added to line
                    if changed_field == "device_ids":
                        old_devices = set(
                            initial_values[changed_field].mapped("imei_no")
                        )
                        new_devices = set(self.device_ids.mapped("imei_no"))
                        if len(old_devices) > len(new_devices):
                            change_status = "removed"
                            changed_device = ", ".join(list(old_devices - new_devices))
                        else:
                            change_status = "added"
                            changed_device = ", ".join(list(new_devices - old_devices))
                        self.message_post(
                            body=f"{changed_device} has been {change_status}.",
                            author_id=self.env.user.partner_id.id,
                        )
                        continue
                    vals = {
                        "field": field.id,
                        "field_desc": field.field_description,
                        "field_type": field.ttype,
                        "tracking_sequence": field.tracking,
                        "old_value_char": ", ".join(
                            initial_values[changed_field].mapped("name")
                        ),
                        "new_value_char": ", ".join(self[changed_field].mapped("name")),
                    }
                    tracking_value_ids.append(Command.create(vals))
        return changes, tracking_value_ids

    def _schedule_activities(self, vals):
        """
        Schedule activities for newly assigned employees in a renewal.

        Args:
            vals (dict): Contains updates for an existing renewal.
        """
        for renewal in self:
            employee_ids = [
                id
                for employee in vals.get("employee_ids", [])
                for id in employee[2]
                if id not in renewal.employee_ids.ids
            ]
            summary = _(f"Renewal {renewal.name} has been assigned.")
            user_ids = self.env["hr.employee"].browse(employee_ids).user_id
            for user_id in user_ids:
                if user_id:
                    self.activity_schedule(
                        "mail.mail_activity_data_todo",
                        user_id=user_id.id,
                        summary=summary,
                    )

    def write(self, vals):
        """
        Updates the renewal record with new values and performs additional actions based on
        the stage transitions. Handles grace period stage, validates device services, creates
        payment date, renewal history, and resets device grace period information when necessary.

        Args:
            vals (dict): A dictionary of field names and their new values to update.

        Returns:
            bool: Returns True if the record was successfully written, False otherwise.
        """
        for renewal in self:
            if "employee_ids" in vals:
                self._schedule_activities(vals)
            grace_period_stage_id = self.stage_id.search(
                [("is_grace_period_stage", "=", True)], limit=1
            ).id
            new_stage_id = vals.get("stage_id", False)
            if new_stage_id and grace_period_stage_id in (
                renewal.stage_id.id,
                new_stage_id,
            ):
                self.handle_grace_period_stage(grace_period_stage_id, new_stage_id)
            if "stage_id" in vals:
                new_stage = self.env["mis.device.renewal.stage"].browse(
                    vals["stage_id"]
                )
                if new_stage.name != "Open":
                    self._validate_idle_after_grace_stage(new_stage)
                    self._validate_device_package()
                    self._validate_device_service()
                if new_stage.is_complete_stage:
                    vals["completed_stage_start_date"] = fields.Datetime.now()
        renewal = super().write(vals)
        for rec in self:
            stage = rec.stage_id
            if "stage_id" in vals and stage.is_payment_stage:
                self.create_payment_date()
            if "stage_id" in vals and (
                stage.is_complete_stage or stage.is_billed_renewed_stage
            ):
                self.create_renewal_history()
            if "stage_id" in vals and stage.is_complete_stage:
                self._reset_device_grace_info()
        return renewal


class MisDeviceRenewalStage(models.Model):
    _name = "mis.device.renewal.stage"
    _description = "MIS Renewal Stage"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=1)
    is_default_stage = fields.Boolean(default=False)
    requirements = fields.Text("Requirements")
    is_payment_stage = fields.Boolean(default=False)
    is_complete_stage = fields.Boolean(default=False)
    is_billed_renewed_stage = fields.Boolean(default=False)
    is_grace_period_stage = fields.Boolean(default=False)
    is_discarded_stage = fields.Boolean(default=False)
    is_idle_stage = fields.Boolean(default=False)
    is_open_stage = fields.Boolean(default=False)
    is_expiry_date_renewal_pi = fields.Boolean(default=False, string="PI expiry date")


class MisDeviceRenewalPackage(models.Model):
    _name = "mis.device.renewal.package"
    _description = "MIS Device Renewal Package"

    name = fields.Char(string="Package Name", required=True)
    addition_period = fields.Char(required=True)
    addition_period_type = fields.Selection(
        selection=[("days", "Days"), ("months", "Months"), ("years", "Years")],
        required=True,
    )
    addition_period_with_type = fields.Char(compute="_compute_complete_addition_period")

    @api.depends("addition_period", "addition_period_type")
    def _compute_complete_addition_period(self):
        """
        Computes the complete addition period by combining the addition period and its type.
        The result is stored in the `addition_period_with_type` field.

        If either the addition period or the addition period type is missing, the result will be None.
        """
        for package in self:
            package.addition_period_with_type = (
                f"{package.addition_period} {package.addition_period_type}"
                if package.addition_period and package.addition_period_type
                else None
            )


class MisDeviceRenewalTags(models.Model):
    _name = "mis.device.renewal.tags"
    _description = "Mis Device Renewal Tags"

    name = fields.Char(string="Name")
    color = fields.Char(string="color")


class MisDeviceRenewalGracePeriod(models.Model):
    _name = "mis.device.renewal.grace.period"
    _description = "Mis Device Renewal Grace Period"

    name = fields.Char(string="Name", required=True)
    period_duration = fields.Integer(string="Duration", required=True)
    is_default = fields.Boolean(string="Default")

    @api.onchange("is_default")
    def _onchange_is_default(self):
        """
        Ensures that only one grace period can be marked as the default.

        If another grace period is already set as default, a UserError is raised,
        prompting the user to remove the existing default before selecting the new one.
        """
        for grace_period in self:
            if grace_period.is_default:
                default_grace_period = self.search([("is_default", "=", True)])
                if default_grace_period:
                    raise UserError(
                        _(
                            f"{default_grace_period.name} is already selected as default, \
                                Please remove it first."
                        )
                    )
