{
    "name": "MIS Blacklist Customers",
    "summary": """
        Manages blacklist customers for mis
        """,
    "description": """
        An odoo Module to manage blacklist customers for mis
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": [
        "base",
        "mail",
        "va_mis",
        "mis_tickets",
        "mis_warranty",
        "mis_device_installation",
        "mis_sale",
        "mis_device_renewal",
        "mis_invoice",
    ],
    "license": "LGPL-3",
    "data": [
        "security/blacklist_request_security.xml",
        "security/blacklist_access_rule.xml",
        "security/ir.model.access.csv",
        "views/blacklist_customer.xml",
        "views/res_partner_view_inherit.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "application": True,
}
