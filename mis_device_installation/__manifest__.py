{
    "name": "MIS Device Installation Module",
    "summary": """
         MIS Module to Manage Installation
        """,
    "description": """
         An odoo module for MIS to Manage Installation
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base", "mail", "va_mis"],
    "data": [
        "security/installation_security.xml",
        "security/installation_record_rule.xml",
        "security/ir.model.access.csv",
        "data/mis_installation_stages.xml",
        "data/cron_inactive_installation.xml",
        "views/installation_views.xml",
        "views/inactive_installation_views.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "application": True,
}
