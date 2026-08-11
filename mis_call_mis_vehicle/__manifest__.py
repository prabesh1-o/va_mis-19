{
    "name": "MIS Call  MIS Vehicle",
    "summary": """
        Manages call  and Vehicle relationship
        """,
    "description": """
        An odoo Module to Manages call  and Vehicle relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_call", "mis_device_mis_vehicle", "mis_vehicle"],
    "data": ["views/mis_call_views_inherit.xml",],
    "auto_install": True,
}
