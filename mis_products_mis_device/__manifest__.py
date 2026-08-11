{
    "name": "MIS Products Mis Device",
    "summary": """
        Manages Mis Products Mis Device
        """,
    "description": """
        An odoo Module to Manages Mis Products Mis Device
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_products", "mis_device"],
    "data": [
        "views/mis_device_views_inherit.xml",
        "views/res_partner_views_inherit.xml",
    ],
    "auto_install": True,
}
