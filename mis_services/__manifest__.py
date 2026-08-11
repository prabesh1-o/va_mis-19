{
    "name": "MIS Services",
    "summary": """
        Manages Services Provided by Company
        """,
    "description": """
        An odoo Module to Manage MIS Services
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mail", "va_mis"],
    "data": [
        "security/mis_service_security.xml",
        "security/ir.model.access.csv",
        "security/mis_service_record_rule.xml",
        "views/mis_services_views.xml",
        "views/mis_services_menu_views.xml",
    ],
    "installable": True,
    "application": True,
}
