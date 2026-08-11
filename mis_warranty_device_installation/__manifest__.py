{
    "name": "MIS Warranty Device Installation",
    "summary": """
        Manages warranty device installation
        """,
    "description": """
        An odoo Module to Manage warranty device installation
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mis_device_warranty", "mis_device_installation",],
    "license": "LGPL-3",
    "data": [
        "views/mis_device_installation_inherit.xml",
        "views/mis_warranty_inherit_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
