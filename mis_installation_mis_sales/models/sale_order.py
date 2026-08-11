from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    installation_ids = fields.One2many(
        "mis.device.installation",
        "sale_order_id",
        string="Installation",
    )

    installation_count = fields.Integer(
        compute="_compute_installation_count",
        string="Installation Count",
    )

    @api.depends("installation_ids")
    def _compute_installation_count(self):
        """Compute total installations including archived ones."""
        installation_obj = self.env["mis.device.installation"].with_context(
            active_test=False
        )

        for order in self:
            order.installation_count = installation_obj.search_count(
                [("sale_order_id", "=", order.id)]
            )

    def action_view_installation(self):
        """Open installation records linked to the Sale Order."""
        self.ensure_one()

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_device_installation.mis_installation_action"
        )

        action["context"] = {
            "search_default_sale_order_id": self.id,
        }

        installation = (
            self.env["mis.device.installation"]
            .with_context(active_test=False)
            .search(
                [("sale_order_id", "=", self.id)],
                limit=1,
            )
        )

        if self.installation_count == 1 and installation:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": installation.id,
                }
            )

            if action.get("views"):
                action["views"] = [
                    (view_id, view_type)
                    for view_id, view_type in action["views"]
                    if view_type == "form"
                ]

        return action

    def action_cancel(self):
        """
        Odoo 19 no longer has sale.order.cancel wizard.

        Before cancelling:
            - Prevent cancellation if any installation is configured.
            - Cancel installation lines.
            - Move installations to the cancelled stage.
        """

        cancelled_stage = self.env[
            "mis.device.installation.stage"
        ].search(
            [("is_canceled_stage", "=", True)],
            limit=1,
        )

        for order in self:

            installations = order.installation_ids.filtered(
                lambda r: not r.stage_id.is_canceled_stage
            )

            if not installations:
                continue

            configured_installations = installations.filtered(
                lambda r: r.configured_status
            )

            if configured_installations:
                raise ValidationError(
                    _(
                        "You cannot cancel this Sales Order because one or more "
                        "installations have already been configured."
                    )
                )

            for installation in installations:

                if installation.installation_line_ids:
                    installation.installation_line_ids.write(
                        {
                            "state": "canceled",
                        }
                    )

                if cancelled_stage:
                    installation.stage_id = cancelled_stage.id

        return super().action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    installation_line_ids = fields.One2many(
        "mis.device.installation.line",
        "sale_order_line_id",
        string="Installation Lines",
    )