{
    "name": " MIS Inventory MIS Installation  MIS Stock Device",
    "summary": """
        Manages Inventory Installation  and Stock Device relationship
        """,
    "description": """
        An odoo Module to Manages Installation  and Device relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_device_installation", "mis_inventory_mis_device", "mis_sale"],
    "data": ["views/installation_views.xml",],
    "auto_install": True,
}
