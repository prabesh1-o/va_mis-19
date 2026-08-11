from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):
    def _get_mandatory_fields_shipping(self, country_id):
        res = super()._get_mandatory_fields_shipping(country_id)
        if "zip" in res:
            res.remove("zip")
        return res

    def _get_mandatory_fields_billing(self, country_id):
        res = super()._get_mandatory_fields_shipping(country_id)
        if "zip" in res:
            res.remove("zip")
        return res
