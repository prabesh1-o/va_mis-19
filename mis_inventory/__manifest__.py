{
    "name": "MIS Inventory",
    "summary": """
        Manages MIS Inventory
        """,
    "description": """
        An odoo Module to Manage Inventory
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "va_mis", "stock"],
    "data": [
        "views/inventory_inherit.xml",
        "views/stock_location_inherit.xml",
        "views/stock_picking_internal.xml",
    ],
    "installable": True,
    "application": True,
}
