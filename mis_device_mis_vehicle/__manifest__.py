{
    "name": "MIS Device Mis Vehicle",
    "summary": """
        Manages Tracmate Mis device  and mis vehicle
        """,
    "description": """
        An odoo Module to Manage Mis device and mis vehicle
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mis_device", "mis_vehicle"],
    "license": "LGPL-3",
    "data": ["views/mis_device_views.xml", "views/fleet_vehicle_views.xml",],
    "auto_install": True,
}
