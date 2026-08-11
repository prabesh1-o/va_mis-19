{
    "name": "MIS Call",
    "summary": """
        Manages calls received
        """,
    "description": """
        An odoo Module to Manage and track the calls received
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["base", "mail", "va_mis"],
    "license": "LGPL-3",
    "data": [
        "security/call_campaign_security.xml",
        "security/assign_call_security.xml",
        "security/assign_call_record_rule.xml",
        "security/call_generator_security.xml",
        "security/campaign_record_rule.xml",
        "security/ir.model.access.csv",
        "views/mis_call.xml",
        "views/res_partner_inherit.xml",
        "views/mis_assign_call.xml",
        "views/mis_call_campaign.xml",
        "views/mis_call_batch.xml",
        "views/mis_call_generator.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "application": True,
}
