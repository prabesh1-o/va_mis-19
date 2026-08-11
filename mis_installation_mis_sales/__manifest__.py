{
    "name": "MIS Installation  MIS Sales",
    "summary": """
        Manages Installation  and Sales relationship
        """,
    "description": """
        An odoo Module to Manages Installation  and Sales relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version": '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_device_installation", "mis_sale"],
    "data": ["views/sale_order_views.xml", "views/mis_device_installation_views.xml",],
    "auto_install": True,
}
