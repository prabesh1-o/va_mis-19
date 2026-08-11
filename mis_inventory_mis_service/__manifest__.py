{
    "name": "MIS Inventory MIS Service",
    "summary": """
        Manages MIS Inventory and MIS Service
        """,
    "description": """
        An odoo Module to Manage Sales from from service and products
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_inventory", "mis_sale"],
    "data": ["security/ir.model.access.csv", "views/sales_order_inherit.xml"],
    "auto_install": True,
}
