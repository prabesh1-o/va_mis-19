{
    "name": "MIS Inventory MIS Sale MIS Installation",
    "summary": """
        Manages MIS Inventory MIS Sale and MIS Installation
        """,
    "description": """
        An odoo Module to Manage Installation from sale and inventory """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_installation_mis_sales", "mis_inventory","sale_stock"],
    "data": ["views/mis_device_installation_inherit.xml"],
    "auto_install": True,
}
