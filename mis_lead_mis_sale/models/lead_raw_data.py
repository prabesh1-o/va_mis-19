from odoo import _, models
from odoo.exceptions import UserError


class LeadRawData(models.Model):
    _inherit = "lead.raw.data"

    def create_partner_with_information(self):
        for lead in self:
            lead.customer_id.write(
                {
                    "email": lead.email,
                    "phone": lead.phone_no,
                    "street": lead.address,
                    "child_ids": [
                        (
                            0,
                            0,
                            {
                                "name": contact_person.name,
                                "email": contact_person.email,
                                "phone": contact_person.phone,
                                "street": contact_person.address,
                            },
                        )
                        for contact_person in lead.contact_person_ids
                        if lead.contact_person_ids
                    ],
                }
            )

    def btn_create_quotation(self):
        for lead in self:
            if lead.remarks == "interested":
                self.create_partner_with_information()
                pricelist_id = (
                    self.env["product.pricelist"].search([("sequence", "=", 1)]).id
                )
                self.env["sale.order"].create(
                    [
                        {
                            "partner_id": lead.customer_id.id,
                            "required_service_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        service_id
                                        for service_id in lead.required_service_ids.ids
                                    ],
                                )
                            ],
                            "pricelist_id": pricelist_id,
                            "raw_lead_id": lead.id,
                            "order_line": [
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": line.service_id.product_product_id.id,
                                        "product_uom_qty": line.quantity,
                                        "price_unit": line.final_price,
                                    },
                                )
                                for line in lead.raw_lead_service_line_ids
                            ],
                        }
                    ]
                )

                lead.state = "quotation"
            else:
                raise UserError(_("The Remark should be interested to continue."))
