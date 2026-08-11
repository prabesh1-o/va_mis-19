{
    "name": "MIS Renewal  MIS Device",
    "summary": """
        Manages Renewal  and Device relationship
        """,
    "description": """
        An odoo Module to Manages Installation  and Device relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_device_renewal", "mis_device_mis_vehicle", "mis_vehicle"],
    "data": ["views/mis_renewal_views_inherit.xml",],
    "auto_install": True,
}
