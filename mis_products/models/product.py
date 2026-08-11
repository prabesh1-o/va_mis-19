from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisProduct(models.Model):
    _name = "mis.product"
    _description = "MIS Products"
    _order = "priority desc, name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    product_type = fields.Many2one("mis.product.type", string="Product Type")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    price = fields.Monetary(
        string="Price",
        currency_field="company_currency_id",
        required=True,
        tracking=True,
    )
    image = fields.Image()
    description = fields.Html(string="Description")
    product_model_ids = fields.One2many(
        "mis.product.model", "product_id", string="Product Models"
    )
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Favorite")], default="0", string="Favorite"
    )

    state = fields.Selection(
        selection=[("active", "Active"), ("inactive", "Inactive")],
        string="Status",
        required=True,
        default="active",
    )
    has_imei = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")], string="IMEI", required=True
    )
    discount_percentage = fields.Float(string="Discount Percentage", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    discounted_price = fields.Monetary(
        currency_field="company_currency_id",
        compute="_compute_discounted_price",
        string="Discounted Price",
    )
    is_product = fields.Boolean(string="Is Product", default=False)
    quantity = fields.Float(string="Quantity", default=1.0)
    price_subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="company_currency_id",
        compute="_compute_price_subtotal",
    )
    active = fields.Boolean(default=True)

    @api.depends("discounted_price", "quantity")
    def _compute_price_subtotal(self):
        for product in self:
            if product.quantity:
                product.price_subtotal = product.discounted_price * product.quantity
            else:
                product.price_subtotal = 0

    @api.depends("price", "discount_percentage")
    def _compute_discounted_price(self):
        for product in self:
            discount_percent = product.discount_percentage
            if discount_percent and product.price:
                if 0 < discount_percent <= 100:
                    product.discounted_price = (
                        product.price - (discount_percent / 100) * product.price
                    )
                else:
                    raise UserError(
                        _("Discount percentage cannot be less than 0 or more than 100.")
                    )
            else:
                product.discounted_price = product.price


class MisProductType(models.Model):
    _name = "mis.product.type"
    _description = "Mis Products Type"

    name = fields.Char(string="Name", required=True)


class MisProductModel(models.Model):
    _name = "mis.product.model"
    _description = "Mis Product Model"

    name = fields.Char(string="name", required=True)
    product_id = fields.Many2one("mis.product", string="Product")
    manufacturer_id = fields.Many2one("mis.manufacturer", string="Manufacturer")
    model_protocol = fields.Char(string="Protocol")
    model_port = fields.Char(string="Port")
