{
    "name": "MIS Products",
    "summary": """
        Manages Tracmate users and devices
        """,
    "description": """
        An odoo Module to Manage Tracmate users and devices
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "va_mis", "mail"],
    "data": [
        "security/product_security.xml",
        "security/ir.model.access.csv",
        "security/product_access_rules.xml",
        "views/product_views.xml",
        "views/supplier_views.xml",
        "views/manufacturer_views.xml",
    ],
    "installable": True,
    "application": True,
}
