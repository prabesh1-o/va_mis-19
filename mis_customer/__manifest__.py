{
    "name": "MIS Customer",
    "summary": """
        Manages customers for mis
        """,
    "description": """
        An odoo module to manage customers for MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["base", "va_mis"],
    "license": "LGPL-3",
    "data": [
        "security/mis_customer_security.xml",
        "security/ir.model.access.csv",
        "security/customer_access_rules.xml",
        "data/customer_industries.xml",
        "views/res_partner_view_inherit.xml",
    ],
    "installable": True,
    "application": True,
}
