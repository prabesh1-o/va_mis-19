from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

FUEL_TYPE_SELECTION = [
    ("diesel", "Diesel"),
    ("gasoline", "Gasoline"),
    ("full_hybrid", "Full Hybrid"),
    ("plugin_diesel", "Plug-in Hybrid Diesel"),
    ("plugin_gasoline", "Plug-in Hybrid Gasoline"),
    ("cng", "CNG"),
    ("lpg", "LPG"),
    ("hydrogen", "Hydrogen"),
    ("electric", "Electric"),
]

VEHICLE_TYPE_SELECTION = [
    ("scooter", "Scooter"),
    ("bike", "Motorbike"),
    ("car", "Car"),
    ("van", "Van"),
    ("jeep", "Jeep"),
    ("truck", "Truck"),
    ("tipper", "Tipper"),
]


class MisVehicle(models.Model):
    _name = "mis.vehicle"
    _description = "MIS Vehicle"
    _rec_name = "vehicle_number"

    vehicle_number = fields.Char(string="Vehicle Number")
    image = fields.Image()
    vin = fields.Char(string="VIN")
    color = fields.Char(string="Colour")
    cubic_capacity = fields.Integer(string="Cubic Capacity(CC)")
    cubic_capacity_taxation = fields.Integer(string="Cubic Capacity Taxation")
    description = fields.Html(string="Vehicle Description")
    vehicle_type = fields.Selection(
        VEHICLE_TYPE_SELECTION, string="Vehicle Type", default="car"
    )

    transport_model = fields.Integer(string="Transport Model")

    manufactured_year = fields.Integer(string="Manufactured Year")
    seat_capacity = fields.Integer(string="Seat Capacity")
    payload_capacity = fields.Integer(string="Payload Capacity")
    engine_no = fields.Char(string="Engine No")
    engine_hours = fields.Char(string="Engine Hours", copy=False)
    model_year = fields.Char(string="Model Year")
    transmission = fields.Selection(
        [("manual", "Manual"), ("auto", "Automatic")], string="Transmission",
    )
    trailer = fields.Boolean(string="Trailer")
    horsepower = fields.Integer(string="Horsepower")
    fuel_type = fields.Selection(FUEL_TYPE_SELECTION, string="Fuel Type")

    is_available = fields.Boolean(default=True)
    tag_ids = fields.Many2many("mis.vehicle.tag", string="Tags")
    active = fields.Boolean(default=True)

    blue_book_no = fields.Char(string="Blue Book No")
    registered_name = fields.Char(
        string="Registered Name",
        help="Person who is registered in bluebook for particular vehicle",
    )
    last_renewal_date = fields.Date(string="Last Renewed On")
    expiry_date = fields.Date(string="Expiry Date")
    registered_on = fields.Date(string="Registered On")
    permitted_area = fields.Char(string="Permitted Area")
    vehicle_company_name = fields.Char(string="Company Name")

    customer_id = fields.Many2one("res.partner", string="Customer")

    @api.constrains("vin", "blue_book_no", "engine_no")
    def _check_unique_constraints(self):
        """
        provides constraints and raises error if the values are duplicated
        """
        validation_messages = {
            "vin": "The VIN is already added to another vehicle!",
            "blue_book_no": "The Blue Book No is already added to another vehicle!",
            "engine_no": "The Engine no is already added to another vehicle",
        }

        for field, validation_message in validation_messages.items():
            if any(
                getattr(record, field)
                and self.search(
                    [("id", "!=", record.id), (field, "=", getattr(record, field))]
                )
                for record in self
            ):
                raise ValidationError(_(validation_message))

    @api.onchange("expiry_date", "last_renewal_date")
    @api.depends("expiry_date", "last_renewal_date")
    def onchange_renewed_expiry_date(self):
        """
        validation for renew data and expiry date
        """
        if self.last_renewal_date and self.expiry_date:
            if self.last_renewal_date > self.expiry_date:
                raise ValidationError(
                    _("Expiry Date cannot be earlier than Last Renewed Date ")
                )

    def return_action_to_open(self):
        """
        To open action while clicking in the button box,gets external id from context
        """

        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(
                    self.env.context, default_vehicle_id=self.id, group_by=False
                ),
                domain=[("vehicle_id", "=", self.id)],
            )
            return res
        return False

    # @api.returns("self", lambda value: value.id)
    def copy(self):
        """
        overrides copy method to change the behaviour of duplicating
        """

        fields = ["name", "license_plate", "vin", "driver_id", "blue_book_no"]
        value = ""
        default = {key: value for key in fields}
        res = super().copy(default)
        return res

    @api.model
    def upcoming_service_date(self):
        """
        method for displaying notification
        """
        user = self.env["res.users"].search([])
        user.notify_info(message="My success message")


class MisVehicleTag(models.Model):
    _name = "mis.vehicle.tag"
    _description = "mis.vehicle.tag"

    name = fields.Char(string="name", required=True)
    color = fields.Char(string="color")

    _sql_constraints = [("unique_name", "unique(name)", "Tag name must be unique!")]
