from odoo import api, fields, models


class MisCallGenerator(models.Model):
    _name = "mis.call.generator"
    _description = "MIS Call Generator"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name")
    flag = fields.Boolean(default=False)
    deadline_date = fields.Date(string="Deadline")
    description = fields.Html(string="Description")
    campaign_id = fields.Many2one("mis.call.campaign", string="Campaign", required=True)
    batch_id = fields.Many2one("mis.call.batch", string="Batch")
    created_by = fields.Many2one(
        "hr.employee",
        string="Created By",
        default=lambda self: self.env.user.employee_id,
    )
    assignee = fields.Many2one("hr.employee", string="Assignee")
    assigned_by = fields.Many2one("hr.employee", string="Assigned By")
    assigned_call_ids = fields.Many2many("mis.assign.call", string="Assigned Calls")

    def action_show_assigned_calls(self):
        """
        Opens the view of all assigned calls related to the current record.
        This method opens a list view of assigned calls that are linked to the
        current 'mis.call.generator' record, based on the 'assigned_call_ids' field.

        Returns:
            dict: Action dictionary to open the assigned calls in a tree and form view.
        """
        return {
            "name": "Assigned Calls",
            "type": "ir.actions.act_window",
            "res_model": "mis.assign.call",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [("id", "in", self.assigned_call_ids.ids)],
        }

    @api.onchange("campaign_id")
    def set_flag(self):
        """
        Sets the 'flag' field based on the selected campaign. This flag controls the visibility
        of the warning in the form view. It checks if there are unresolved calls linked to the
        selected campaign and model, and sets the flag to True or False accordingly.
        """
        active_model_id = self.env.context.get("default_active_model_id")
        active_ids = self.env.context.get("default_active_ids", [])
        call_rec_domain = [
            ("campaign_id", "=", self.campaign_id.id),
            ("source_model_id", "=", active_model_id),
            ("source_record_id", "in", active_ids),
            ("is_resolved", "=", False),
        ]
        existing_call_recs = self.env["mis.assign.call"].search(call_rec_domain)
        self.flag = True if existing_call_recs else False

    def assign_calls(self, record, model_id, record_ids, batch):
        """
        Assigns calls to the selected records in the given model. It fetches the selected records,
        prepares the call data, and creates calls if necessary.

        Args:
            record (mis.call.generator): The current call generator record.
            model_id (int): The ID of the model to assign calls from.
            record_ids (list): List of record IDs from the model to assign calls to.
        """
        selected_records = self._fetch_records(model_id, record_ids)
        calls_to_create = self._prepare_calls(record, model_id, selected_records, batch)
        if calls_to_create:
            self._create_calls(record, calls_to_create)

    def _fetch_records(self, model_id, record_ids):
        """
        Fetches records from the specified model and record IDs.

        Args:
            model_id (int): The model ID from which to fetch records.
            record_ids (list): List of record IDs to retrieve.

        Returns:
            recordset: A recordset of the specified model containing the given records.
        """
        model_name = self.env["ir.model"].browse(model_id).model
        return self.env[model_name].browse(record_ids)

    def _prepare_calls(self, record, model_id, records, batch):
        """
        Prepares the data for calls to be created based on the provided records. This method checks
        for existing calls and ensures that only unresolved calls are considered for creation.

        Args:
            record (mis.call.generator): The call generator record containing relevant details.
            model_id (int): The model ID for the records being processed.
            records (recordset): The selected records for which calls are to be created.

        Returns:
            list: A list of dictionaries containing the data for new calls to be created.
        """
        domain = [
            ("campaign_id", "=", record.campaign_id.id),
            ("source_model_id", "=", model_id),
            ("source_record_id", "in", records.ids),
            ("is_resolved", "=", False),
        ]
        existing_calls = self.env["mis.assign.call"].search(domain)
        existing_call_map = {
            (call.source_model_id.id, call.source_record_id): call
            for call in existing_calls
        }
        to_create_calls = []
        model = self.env["ir.model"].browse(model_id)
        for rec in records:
            existing_call = existing_call_map.get((model_id, rec.id))
            customer_ids = (
                rec.ids
                if model.model == "res.partner"
                else self._extract_partner_ids(rec)
            )
            for customer_id in customer_ids:
                if customer_id and (not existing_call or existing_call.is_resolved):
                    to_create_calls.append(
                        {
                            "customer_id": customer_id,
                            "campaign_id": record.campaign_id.id,
                            "batch_id": batch.id,
                            "description": model.name,
                            "source_model_id": model_id,
                            "source_record_id": rec.id,
                            "assignee": record.assignee.id,
                            "assigned_by": record.assigned_by.id,
                            "deadline_date": record.deadline_date,
                        }
                    )
        return to_create_calls

    def _extract_partner_ids(self, record):
        """
        Extracts the partner IDs from the provided record. This method checks common fields in
        the record that might store partner IDs and returns them as a list.

        Args:
            record (recordset): The record from which to extract partner IDs.

        Returns:
            list: A list of partner IDs.
        """
        partner_fields = ["customer_id", "partner_id", "customer_ids", "partner_ids"]
        for field in partner_fields:
            if hasattr(record, field):
                value = getattr(record, field)
                if isinstance(value, (int, bool)) and value:
                    return [value]
                if hasattr(value, "ids"):
                    return value.ids
        return []

    def _create_calls(self, record, call_data):
        """
        Creates new assigned calls and links them to the current record. It creates the calls
        based on the prepared data and assigns them to the 'assigned_call_ids' field of the
        call generator record.

        Args:
            record (mis.call.generator): The call generator record to which the calls will be linked.
            call_data (list): A list of dictionaries containing the data for creating new calls.
        """
        assign_call_ids = self.env["mis.assign.call"].create(call_data).ids
        record.assigned_call_ids = [(4, call_id) for call_id in assign_call_ids]

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        context = self.env.context
        active_ids = context.get("default_active_ids", [])
        active_model_id = context.get("default_active_model_id")
        if active_ids and active_model_id:
            batch = self.env["mis.call.batch"].create(
                {"campaign_id": record.campaign_id.id,}
            )
            self.assign_calls(record, active_model_id, active_ids, batch)
        return record
