{
    "name": "MIS Device Warranty Invoice",
    "summary": """
        Manages device warranty invoices
        """,
    "description": """
        An odoo Module to Manage device warranty
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mis_device_warranty", "mis_invoice"],
    "license": "LGPL-3",
    "data": ["views/account_move_inherit.xml", "views/mis_warranty_inherit_view.xml",],
    "installable": True,
    "application": False,
    "auto_install": True,
}
