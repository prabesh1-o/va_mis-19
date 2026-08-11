from odoo import _, fields, models
from odoo.exceptions import UserError


class MisWarrantyPackage(models.Model):
    _inherit = "mis.warranty.package"

    product_id = fields.Many2one("mis.product")

    def btn_create_product(self):
        self.ensure_one()
        if self.product_id:
            raise UserError(_("Product is already created!"))
        product_type = self.env["mis.product.type"].search(
            [("name", "=", "Warranty")], limit=1
        )
        if not product_type:
            product_type = self.env["mis.product.type"].create({"name": "Warranty"})
        product = self.env["mis.product"].create(
            {
                "name": self.name,
                "has_imei": "no",
                "is_product": False,
                "detailed_type": "consu",
                "price": 0,
                "product_type": product_type.id,
                "warranty_package_id": self.id,
            }
        )
        self.product_id = product

    def action_view_product(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_products.mis_product_action"
        )
        action["domain"] = [("warranty_package_id", "=", self.id)]
        action["view_mode"] = "form"
        action["res_id"] = self.product_id.id
        if "views" in action:
            action["views"] = [
                (view_id, view_type)
                for view_id, view_type in action["views"]
                if view_type == "form"
            ]
        return action
