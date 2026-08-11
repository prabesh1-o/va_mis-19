{
    "name": "MIS Warranty Inventory",
    "summary": """
        Manages device warranty and inventory
        """,
    "description": """
        An odoo Module to Manage device warranty and inventory
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": [
        "mis_device_warranty",
        "mis_inventory_mis_device",
        "mis_device_installation",
        "mis_warranty_device_installation",
    ],
    "license": "LGPL-3",
    "data": [
        "views/mis_warranty_view_inherit.xml",
        "views/mis_device_installation_inherit.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
