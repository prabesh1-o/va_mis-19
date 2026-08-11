{
    "name": "MIS Warranty Product",
    "summary": """
        Manages warranty product
        """,
    "description": """
        An odoo Module to Manage warranty product
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mis_warranty", "mis_products"],
    "license": "LGPL-3",
    "data": ["views/mis_warranty_package_inherit.xml",],
    "installable": True,
    "application": False,
    "auto_install": True,
}
