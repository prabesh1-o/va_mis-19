from odoo import api, fields, models


class MisReseller(models.Model):
    _name = "mis.reseller"
    _description = "Mis Reseller"

    name = fields.Char(string="Name", required=True)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP")
    state_id = fields.Many2one(
        "res.country.state", string="State", domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one("res.country", string="Country")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")
    vat = fields.Char(string="VAT Number")
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)
    is_reseller = fields.Boolean(default=True, string="Is Reseller")
    device_count = fields.Integer(compute="_compute_device_count", string="Devices")
    partner_id = fields.Many2one(
        "res.partner", string="Related Partner", ondelete="cascade"
    )
    related_location_id = fields.Many2one(
        "stock.location", readonly=True, string="Reseller Location"
    )

    sale_order_ids = fields.One2many("sale.order", "reseller_id", string="Sales Orders")
    invoice_ids = fields.One2many(
        "account.move",
        "reseller_id",
        string="Invoices",
        domain=[("move_type", "=", "out_invoice")],
    )
    delivery_ids = fields.One2many(
        "stock.picking",
        "reseller_id",
        string="Deliveries",
        domain=[("picking_type_id.code", "=", "outgoing")],
    )

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def _prepare_partner_values(self, res):
        partner_vals = {
            "name": res.name,
            "street": res.street,
            "street2": res.street2,
            "city": res.city,
            "zip": res.zip,
            "state_id": res.state_id.id,
            "country_id": res.country_id.id,
            "phone": res.phone,
            # "mobile": res.mobile,
            "email": res.email,
            "website": res.website,
            "vat": res.vat,
            "is_reseller": True,
            "is_customer": False,
        }
        return partner_vals

    def _create_internal_location(self):
        self.ensure_one()
        if not self.related_location_id:
            warehouse = self.env.ref("stock.warehouse0")
            location_values = {
                "location_id": warehouse.view_location_id.id,
                "name": f"Resellers/{self.name}/{self.id}",
                "usage": "internal",
                "company_id": self.env.company.id,
            }
            location = self.env["stock.location"].create(location_values)
            self.related_location_id = location.id

    @api.model
    def create(self, vals):
        """
        creates a new reseller record and a res partner record.
        creates a new internal location with the reseller name
        """
        res = super().create(vals)
        partner_vals = self._prepare_partner_values(res)
        partner = self.env["res.partner"].create(partner_vals)
        res.partner_id = partner.id
        res._create_internal_location()
        return res

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.partner_id:
                updated_vals = record._prepare_partner_values(record)
                record.partner_id.write(updated_vals)
        return res

    def unlink(self):
        partners = self.mapped("partner_id")
        res = super().unlink()
        if partners:
            partners.unlink()
        return res

    def btn_create_sale_order(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Create Sales Order",
            "res_model": "sale.order",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_partner_invoice_id": self.partner_id.id,
                "default_reseller_id": self.id,
                "default_is_reseller_order":True,
            },
        }

    def _compute_device_count(self):
        for record in self:
            if record.related_location_id:
                inventory_device = self.env["mis.inventory.device"]
                device_count = inventory_device.search_count(
                    [("location_id", "=", record.related_location_id.id)]
                )
                record.device_count = device_count
            else:
                record.device_count = 0

    def action_view_devices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Mis Inventory Devices",
            "res_model": "mis.inventory.device",
            "view_mode": "list,form",
            "domain": [("location_id", "=", self.related_location_id.id)],
            "context": {
                "search_default_location_id": self.related_location_id.id,
                "create": False,
                "edit": True,
            },
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Reseller Quotations",
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": [
                ("reseller_id", "=", self.id),
                ("is_reseller_order", "=", True),
            ],
            "context": {
                "default_reseller_id": self.id,
                "default_is_reseller_order": True,
                },
        }


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_reseller = fields.Boolean(string="Is Reseller", default=False)
