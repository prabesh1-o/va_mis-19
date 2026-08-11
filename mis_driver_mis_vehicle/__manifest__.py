{
    "name": "MIS driver  MIS Vehicle",
    "summary": """
        Manages driver  and vehicle relationship
        """,
    "description": """
        An odoo Module to Manages Driver  and Vehicle relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_driver", "mis_vehicle"],
    "data": [
        "security/ir.model.access.csv",
        "views/vehicle_views_inherit.xml",
        "views/driver_views_inherit.xml",
        "views/driver_history_views.xml",
    ],
    "auto_install": True,
}
