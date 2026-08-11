{
    "name": "MIS Device Warranty",
    "summary": """
        Manages device warranty
        """,
    "description": """
        An odoo Module to Manage device warranty
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mis_device", "mis_warranty"],
    "license": "LGPL-3",
    "data": [
        "views/mis_device_inherit_view.xml",
        "views/mis_warranty_inherit_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
