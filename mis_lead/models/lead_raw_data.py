import ast

from odoo import _, fields, models
from odoo.exceptions import UserError


class LeadRawData(models.Model):
    _name = "lead.raw.data"
    _description = "Lead Raw Data"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _rec_name = "customer_id"

    is_company = fields.Selection(
        selection=[("individual", "Individual"), ("company", "Company")],
        default="individual",
    )
    customer_id = fields.Many2one("res.partner", string="Client")
    company_name = fields.Char(string="Company Name")
    email = fields.Char(string="E-mail")
    phone_no = fields.Char(string="Phone No.")
    address = fields.Char(string="Address")
    campaign_id = fields.Many2one(
        "lead.raw.data.campaign", string="Campaign", tracking=True
    )
    industry_id = fields.Many2one(
        "lead.raw.data.industry", string="Industry", tracking=True
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    is_existing_gps_user = fields.Boolean(
        default=False,
        string="Existing GPS User",
        help="Tick If user is already using GPS from any other company",
    )
    gps_company_name = fields.Char(
        string="GPS Company Name",
        help="Name of The GPS company that specific raw lead is client of ",
    )
    existing_renewal_price = fields.Monetary(
        currency_field="company_currency_id",
        string="Renewal Price",
        help="The GPS companies current Renewal Rate",
    )
    no_of_vehicle = fields.Integer(string="No of Vehicle")
    remarks = fields.Selection(
        selection=[
            ("not_interested", "Not Interested"),
            ("interested", "Interested"),
            ("follow_up", "Follow Up"),
        ],
        tracking=True,
    )
    lost_reason = fields.Char(string="Lost Reason")
    total_amount = fields.Monetary(
        compute="_compute_total_amount",
        currency_field="company_currency_id",
        string="Total Amount",
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[("open", "Open"), ("quotation", "Quotation"), ("lost", "Lost"),],
        default="open",
        tracking=True,
    )
    medium_id = fields.Many2one("lead.raw.data.medium", string="Medium")
    contact_person_ids = fields.One2many(
        "lead.point.of.contact", "lead_id", string="Contact Person"
    )
    internal_note = fields.Html(string="Internal Note", sanitize=True)

    def btn_lost_lead(self):
        for lead in self:
            if not lead.remarks and not lead.lost_reason:
                raise UserError(_("Please Add Remarks and Lost Reason First"))
            lead.state = "lost"


class LeadPointOfContact(models.Model):
    _name = "lead.point.of.contact"
    _description = "Lead Point Of Contact"

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    address = fields.Char(string="Address")
    lead_id = fields.Many2one("lead.raw.data")


class LeadRawDataMedium(models.Model):
    _name = "lead.raw.data.medium"
    _description = "Lead Raw Data Medium"

    name = fields.Char(required=True)


class LeadRawDataCampaign(models.Model):
    _name = "lead.raw.data.campaign"
    _description = "Lead Raw Data Campaign"

    name = fields.Char(required=True)

    def mis_raw_lead_actions(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mis_lead.action_lead_raw_data_kanban"
        )
        action["display_name"] = _("%(name)s", name=self.name)
        context = ast.literal_eval(action["context"].replace("active_id", str(self.id)))
        action["view_mode"] = "kanban,tree,form"
        action["context"] = context
        return action


class LeadRawDataIndustry(models.Model):
    _name = "lead.raw.data.industry"
    _description = "Lead Raw Data Industry"

    name = fields.Char(required=True)
