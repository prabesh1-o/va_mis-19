{
    "name": "MIS Inventory MIS Device",
    "summary": """
        Manages MIS Inventory and MIS Device
        """,
    "description": """
        An odoo Module to Manage Device from from Inventory
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_inventory", "mis_device", "mis_products"],
    "data": [
        "views/inventory_internal_inherit.xml",
        "security/ir.model.access.csv",
        "views/base_product_inherit.xml",
        "views/stock_location_inherit.xml",
        "views/stock_devices.xml",
        "views/stock_sim.xml",
    ],
    "installable": True,
    "application": True,
}
