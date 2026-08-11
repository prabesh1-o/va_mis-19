from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MisDevice(models.Model):
    _inherit = "mis.device"

    def _get_default_grace_period(self):
        return (
            self.env["mis.device.renewal.grace.period"]
            .search([("is_default", "=", True)])
            .id
            or None
        )

    def _get_tax_id(self):
        return (
            self.env["account.tax"].search([("active", "=", True)], limit=1).id or None
        )

    renewal_price = fields.Monetary(
        currency_field="company_currency_id", group_operator="sum"
    )
    current_renewal_price = fields.Monetary(
        currency_field="company_currency_id",
        group_operator="sum",
        string="Renewal Price",
        compute="_compute_current_renewal_price",
        store=True,
    )
    renewal_tax_string = fields.Char(compute="_compute_renewal_tax_string")
    payment_date = fields.Date(string="Payment Date")
    device_model_id = fields.Many2one("mis.product.model", string="Model")
    grace_period_id = fields.Many2one(
        "mis.device.renewal.grace.period",
        string="Grace Period",
        default=_get_default_grace_period,
    )
    grace_period_start = fields.Date(string="Grace Period Start")
    grace_period_end = fields.Date(string="Grace Period End")
    grace_period_days_count = fields.Integer(string="Grace Period Days")
    grace_period_count = fields.Integer(
        compute="_compute_grace_period_count", string="Grace Period Count"
    )
    total_time_grace_period = fields.Integer()
    renewal_package_id = fields.Many2one(
        "mis.device.renewal.package", string="Renewal Package"
    )
    device_renewal_history_id = fields.One2many(
        "mis.device.renewal.history", "device_id"
    )
    renewal_history_count = fields.Integer(
        compute="_compute_device_renewal_history_count"
    )
    expiration_time = fields.Date(
        compute="_compute_expiration_time_from_renewal_history",
        store=True,
        readonly=False,
    )
    exp_expiration_date = fields.Date(string="Expected Expiration")
    expiry_date_type = fields.Selection(
        selection=[("automatic", "Automatic"), ("manual", "Manual")],
        string="Expiry Date Type",
        default="automatic",
        required=True,
    )
    tax_id = fields.Many2one("account.tax", string="Tax", default=_get_tax_id)
    tax_amount = fields.Monetary(
        compute="_compute_price",
        currency_field="company_currency_id",
        group_operator="sum",
        store="True",
    )
    price_subtotal = fields.Monetary(
        compute="_compute_price",
        currency_field="company_currency_id",
        group_operator="sum",
        string="Total",
        store=True,
    )

    @api.depends("renewal_price", "expiry_date_type", "expiration_time","renewal_package_id")
    def _compute_current_renewal_price(self):
        """
        Computes the `current_renewal_price` for each device based on its expiry type.

        - If the expiry type is "manual", it ensures the expiration date is not in the past
        and calculates the renewal price per day using the renewal package's period.
        - If the expiry type is not "manual", it directly assigns the standard renewal price.
        """
        for device in self:
            today = datetime.now().date()
            if device.expiry_date_type == "manual":
                if device.exp_expiration_date and device.exp_expiration_date < today:
                    raise UserError(_("Expiry date cannot be set before today."))
                renewal_package = device.renewal_package_id
                if renewal_package and device.expiration_time:
                    addition_period = int(renewal_package.addition_period)
                    addition_period_type = renewal_package.addition_period_type
                    delta_mapping = {
                        "days": relativedelta(days=addition_period),
                        "months": relativedelta(months=addition_period),
                        "years": relativedelta(years=addition_period),
                    }
                    package = delta_mapping.get(addition_period_type, relativedelta())
                    package_days = (
                        (device.expiration_time + package) - device.expiration_time
                    ).days
                    renewal_price_per_day = device.renewal_price / package_days
                    device.current_renewal_price = self._compute_manual_renewal_charge(
                        renewal_price_per_day, today
                    )
                device.current_renewal_price = device.renewal_price
            else:
                device.current_renewal_price = device.renewal_price

    def _compute_manual_renewal_charge(self, unit_price, today):
        """
        Calculates the manual renewal charge based on the difference in expiration dates and grace period.

        If the expiration date is not exceeded, it computes the charge for the remaining days.
        If the expiration date is in the past, it includes the grace period and calculates the charge
        based on the adjusted number of days.
        """
        for device in self:
            if device.expiration_time >= today:
                days = (device.exp_expiration_date - device.expiration_time).days
                return days * unit_price
            expired_days_count = (today - device.expiration_time).days
            grace_period = (
                expired_days_count
                if device.grace_period_days_count > expired_days_count
                else device.grace_period_days_count
            )
            days = (device.exp_expiration_date - today).days + grace_period
            return days * unit_price

    def _compute_renewal_tax_string(self):
        """
        Computes and updates the `renewal_tax_string` for each device.

        - If the device has a tax and a renewal price, it calculates the total price
        including tax and formats it as a string.
        - If no tax or renewal price is present, the tax string is set to None.
        """
        for device in self:
            if device.tax_id and device.renewal_price:
                price = device.renewal_price + (
                    (device.tax_id.amount / 100) * device.renewal_price
                )
                device.renewal_tax_string = f"(= Rs {round(price, 2):,} Incl. Taxes)"
            else:
                device.renewal_tax_string = None

    @api.onchange("tax_id", "renewal_price", "current_renewal_price")
    @api.depends("tax_id", "renewal_price", "current_renewal_price")
    def _compute_price(self):
        """
        Computes and updates the `price_subtotal` and `tax_amount` for each device.

        - `price_subtotal` is calculated by adding the tax amount to the `current_renewal_price`.
        - `tax_amount` is derived as the difference between `price_subtotal` and `current_renewal_price`.
        """
        for device in self:
            renewal_price = device.current_renewal_price
            device.price_subtotal = (
                renewal_price + (device.tax_id.amount * renewal_price) / 100
            )
            device.tax_amount = device.price_subtotal - renewal_price

    @api.depends("device_renewal_history_id")
    def _compute_expiration_time_from_renewal_history(self):
        """
        Computes and updates the `expiration_time` and `state` based on the latest
        renewal history record.

        - Finds the most recent `expiry_date` from `device_renewal_history_id`.
        - Updates `expiration_time` with this date.
        - Sets `state` to "active" if the new expiration time is in the future,
        otherwise sets it to "inactive".
        """
        for device in self:
            renewal_history = device.device_renewal_history_id
            new_expiry_date = renewal_history.filtered(
                lambda r: r.id == max(renewal_history.mapped("id"))
            ).expiry_date
            if new_expiry_date:
                device.expiration_time = new_expiry_date
                device.state = (
                    "active" if new_expiry_date > datetime.now().date() else "inactive"
                )

    def compute_expiry_date(self):
        """
        Computes and updates the expiration date (`exp_expiration_date`) for each device.
        It considers the renewal package, extension period, and grace period, adjusting the
        expiration date accordingly based on whether the device is still valid
        or already expired.
        """
        for device in self:
            if device.expiry_date_type == "automatic":
                today = datetime.now().date()
                renewal_package = device.renewal_package_id
                addition_period = int(renewal_package.addition_period)
                addition_period_type = renewal_package.addition_period_type
                delta_mapping = {
                    "days": relativedelta(days=addition_period),
                    "months": relativedelta(months=addition_period),
                    "years": relativedelta(years=addition_period),
                }
                if renewal_package:
                    extension_period = delta_mapping.get(
                        addition_period_type, relativedelta()
                    )
                    grace_period = relativedelta(days=device.grace_period_days_count)
                    if device.expiration_time >= today:
                        device.exp_expiration_date = (
                            device.expiration_time + extension_period
                        )
                    else:
                        expired_days_count = (today - device.expiration_time).days
                        if device.grace_period_days_count > expired_days_count:
                            grace_period = relativedelta(days=expired_days_count)
                        device.exp_expiration_date = (
                            today + extension_period - grace_period
                        )
                else:
                    device.exp_expiration_date = device.expiration_time

    @api.onchange("price_subtotal")
    def _compute_unit_price(self):
        """
        Computes and updates the `renewal_price` based on `price_subtotal`.

        - If `current_renewal_price` remains unchanged, the method calculates the
        `renewal_price` by removing tax (if applicable) from `price_subtotal`.
        """
        for device in self:
            if device.current_renewal_price == device._origin.current_renewal_price:
                if device.tax_id:
                    device.renewal_price = device.price_subtotal / (
                        1 + (device.tax_id.amount / 100)
                    )
                else:
                    device.renewal_price = device.price_subtotal

    def _compute_is_expired(self, device):
        """
        Determine whether the given device is expired.
        A device is considered expired if its expiration_time is set and is earlier
        than today's date.

        Args:
            device: An object representing the device, expected to have an
            `expiration_time` attribute.

        Returns:
            bool: True if the device is expired, False otherwise.
        """
        today = datetime.now().date()
        return device.expiration_time < today if device.expiration_time else False

    def compute_grace_days_count(self, date_field, device):
        """
        Calculate the number of grace days between a given date and the device's
        expiration or grace period start time.

        The function calculates how many days have passed since the device's expiration
        time or grace period start time, depending on the idle grace period.
        If the grace period idle is positive, it computes the days since expiration time.
        Otherwise, it calculates the days since the grace period start time.

        Args:
            date_field (datetime): The date to compare against the device's
            expiration or grace period start time.
            device (object): A device object that contains the expiration_time
            and grace_period_start attributes.

        Returns:
            int: The number of grace days between the provided date and the device's
            expiration or grace period start time.
        """
        grace_period_idle = (device.expiration_time - device.grace_period_start).days
        days_count = (
            (date_field - device.expiration_time).days
            if grace_period_idle > 0
            else (date_field - device.grace_period_start).days
        )
        return days_count

    @api.depends("grace_period_start", "grace_period_end")
    def _compute_grace_period_count(self):
        """
        Computes the grace period count for each device, depending on the current date
        and the device's grace period settings.

        This method calculates the number of grace days for each device by comparing
        the current date with the device's expiration time and grace period.
        If the device has a grace period start time and is expired, the grace period count
        is computed using the `compute_grace_days_count` method.
        Otherwise, the grace period count is set to 0.

        The method is triggered when there is a change in the grace_period_start
        or grace_period_end fields.

        Args:
            None (Method is decorated with @api.depends, so it automatically tracks
            changes in the relevant fields).

        Returns:
            None (The method updates the `grace_period_count` field for each device).
        """
        today = datetime.now().date()
        for device in self:
            is_expired = self._compute_is_expired(device)
            if device.grace_period_start and is_expired:
                device.grace_period_count = self.compute_grace_days_count(today, device)
            else:
                device.grace_period_count = 0

    def _compute_device_renewal_history_count(self):
        """
        Computes and updates the `renewal_history_count` for each device.

        - Sets the count based on the number of records in `device_renewal_history_id`.
        """
        for device in self:
            device.renewal_history_count = len(device.device_renewal_history_id)

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
                    self.env.context, default_device_id=self.id, group_by=False
                ),
                domain=[("device_id", "=", self.id)],
            )
            return res
        return False
