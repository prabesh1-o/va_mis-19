import datetime

from odoo import api, fields, models


class MisCall(models.Model):
    _name = "mis.call"
    _description = "MIS Calls"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "call_id"

    call_id = fields.Char(string="Call Id.", readonly=True)
    reporter = fields.Char(string="Client", required=True)
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        domain=lambda self: [("is_customer", "=", True),],
        tracking=True,
    )

    state = fields.Selection(
        [("incoming", "Incoming"), ("outgoing", "Outgoing")],
        string="State",
        default="incoming",
        required=True,
    )
    number = fields.Char(string="Phone number", required=True)
    time = fields.Datetime(
        string="Time", required=True, default=lambda self: fields.Datetime.now()
    )
    call_duration = fields.Float(string="Call duration", required=True)
    user_id = fields.Many2one("hr.employee", string="Salesperson", tracking=True)
    employee = fields.Many2one(
        "hr.employee",
        "Employee",
        store=True,
        default=lambda self: self.env.user.employee_id,
        required=True,
    )

    department_id = fields.Many2one("hr.department", "Department", store=True,)
    description = fields.Html(string="Description", tracking=True, sanitize=True)
    category = fields.Selection(
        [("inquiry", "Inquiry"),], string="Category", required=True, default="inquiry"
    )

    def _generate_call_id(self):
        """
        Generate a unique call ID based on the previous call ID and the current date.

        If there is a recent call created on the same day, the call ID will be incremented
        from the previous call ID. Otherwise, a new call ID will be created based on the
        current date.

        Returns:
            str: The generated call ID.
        """
        recent_call = self.search([], order="id desc", limit=1, offset=1)
        if recent_call and (self._is_todays_call(recent_call)):
            recent_call_id = recent_call.call_id
            call_parts = [recent_call_id[0]]
            call_parts.extend(
                [recent_call_id[i : i + 2] for i in range(1, len(recent_call_id), 2)]
            )
            call_parts[-1] = str(int(call_parts[-1]) + 1)
            call_id = "".join(call_parts)
            return call_id
        else:
            return self._create_new_call_id()

    def _is_todays_call(self, call):
        """
        Check if a given call record was created on the current date.

        Args:
            call (mis.call): The call record to check.

        Returns:
            bool: True if the call was created on the current date, False otherwise.
        """
        return call.create_date.date() == datetime.date.today()

    def _create_new_call_id(self):
        """
        Create a new call ID based on the current date.

        Returns:
            str: The new call ID in the format 'Cyymmdd1'.
        """
        current_date = datetime.datetime.now().strftime("%y%m%d")
        return f"C{current_date}1"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create multiple call records and generate a unique call ID for each record.

        Overrides the `create` method to automatically generate a call ID for each
        new call record before creating it.

        Args:
            vals_list (list): A list of dictionaries containing the field values
                            for the new call records.

        Returns:
            mis.call: A recordset of the newly created call records.
        """
        calls = super().create(vals_list)
        for call in calls:
            call.call_id = self._generate_call_id()
        return calls

    @api.onchange("employee")
    def _onchange_employee(self):
        """
        Updates the 'department_id' field based on the selected employee.
        If no employee is selected, it resets the 'department_id' to None.
        """
        for call in self:
            if call.employee:
                call.department_id = call.employee.department_id
            else:
                call.department_id = None
