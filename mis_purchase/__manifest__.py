{
    "name": "MIS Purchase",
    "summary": """
        Manages Mis Purchases
        """,
    "description": """
        An odoo Module to Manage Purchases from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "va_mis", "mail", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_menuitem.xml",
        "security/purchase_order_record_rules.xml",
    ],
    "installable": True,
    "application": True,
}
