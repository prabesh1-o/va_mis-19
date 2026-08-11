{
    "name": "MIS Lead Module",
    "summary": """
        Mis Lead Module for CRM
        """,
    "description": """
        An odoo Module to manage leads and crm related activities
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mail", "va_mis"],
    "data": [
        "security/mis_lead_security.xml",
        "security/mis_lead_campaign.xml",
        "security/lead_record_rule.xml",
        "security/ir.model.access.csv",
        "views/lead_raw_data_views.xml",
        "views/campaigns_views.xml",
    ],
    "installable": True,
    "application": True,
}
