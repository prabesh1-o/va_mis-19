from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            if not self.env.user.has_group("stock.group_stock_manager"):
                self._check_user_permission(picking)
        return super().button_validate()

    def _check_user_permission(self, picking):
        if picking.picking_type_id.code == "outgoing":
            if (
                picking.location_id
                and self.env.user not in picking.location_id.user_ids
            ):
                raise UserError(
                    _(
                        "You do not have permission to validate this delivery from'%s'."
                        % (picking.location_id.display_name)
                    )
                )

    @api.onchange("location_id")
    def _onchange_location_id(self):
        if self.picking_type_id.code == "outgoing":
            for line in self.move_line_ids:
                line.location_id = self.location_id
