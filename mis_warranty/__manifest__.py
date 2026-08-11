{
    "name": "MIS Warranty",
    "summary": """
        Manages warranty
        """,
    "description": """
        An odoo Module to Manage warranty
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["base", "mail", "va_mis"],
    "license": "LGPL-3",
    "data": [
        "security/warranty_security.xml",
        "security/warranty_record_rule.xml",
        "security/warranty_package.xml",
        "security/ir.model.access.csv",
        "views/mis_warranty_view.xml",
        "views/mis_warranty_package_view.xml",
    ],
    "installable": True,
    "application": True,
}
