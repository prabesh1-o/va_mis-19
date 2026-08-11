{
    "name": "MIS Installation  MIS Device",
    "summary": """
        Manages Installation  and Device relationship
        """,
    "description": """
        An odoo Module to Manages Installation  and Device relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_device_installation", "mis_device", "mis_vehicle"],
    "data": [
        "security/ir.model.access.csv",
        "views/mis_device_views_inherit.xml",
        "views/mis_vehicle_views_inherit.xml",
        "views/mis_installation_views_inherit.xml",
        "views/installation_history_views.xml",
        "views/mis_sim_device_history_views.xml",
        "views/mis_device_sim.xml",
    ],
    "auto_install": True,
}
