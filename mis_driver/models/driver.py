from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisDriver(models.Model):
    _name = "mis.driver"
    _description = "Mis Driver"

    name = fields.Char(string="Name", required=True)
    address = fields.Char(string="Address")
    country_id = fields.Many2one("res.country", string="Country")
    contact_no = fields.Char(string="Contact No.", required=True)
    date_of_birth = fields.Date(string="Date Of Birth")
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("others", "Others"),],
        string="Gender",
        required=True,
    )
    image = fields.Image()
    tag_ids = fields.Many2many("mis.driver.tag", string="Tags")
    description = fields.Html(string="Driver Description")

    license_no = fields.Char(string="License No", required=True)
    registered_address = fields.Char(string="Registered Address")
    registered_date = fields.Date(string="Registered Date")
    allowed_vehicles = fields.Char(string="Allowed Vehicles")
    expiry_date = fields.Date(string="Expiry Date", required=True)

    contract_type = fields.Selection(
        [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("yearly", "Yearly"),
        ],
        string="Contract Type",
    )

    @api.constrains("contact_no", "license_no")
    def _check_unique_constraints(self):
        validation_messages = {
            "contact_no": "The Contact No is already added to existing Driver!",
            "license_no": "The License No is already added to existing Driver!",
        }

        for field, validation_message in validation_messages.items():
            if any(
                getattr(record, field)
                and self.search(
                    [("id", "!=", record.id), (field, "=", getattr(record, field))]
                )
                for record in self
            ):
                raise ValidationError(validation_message)

    @api.onchange("name", "contact_no")
    def _check_numeric_values(self):
        if self.name and any(char.isdigit() for char in self.name):
            raise ValidationError(_("Name cannot contain numeric characters."))
        if self.contact_no and any(char.isalpha() for char in self.contact_no):
            raise ValidationError(_("Contact No. cannot contain alphabet characters."))

    def return_action_to_open(self):
        """
        To open action while clicking in the button box,
        gets external id from context
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(
                    self.env.context, default_driver_id=self.id, group_by=False
                ),
                domain=[("driver_id", "=", self.id)],
            )
            return res
        return False

    # @api.returns("self", lambda value: value.id)
    def copy(self):
        fields = ["name", "contact_no", "license_no"]
        value = ""
        default = {key: value for key in fields}
        res = super().copy(default)
        return res


class FleetDriverTag(models.Model):
    _name = "mis.driver.tag"
    _description = "fleet.driver.tag"

    name = fields.Char(string="name")
    color = fields.Char(string="color")

    _sql_constraints = [("unique_name", "unique(name)", "Tag name must be unique!")]
