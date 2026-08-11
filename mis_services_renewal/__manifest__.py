{
    "name": "MIS Services Renewal",
    "summary": """
        Manages Services  and Renewal relationship
        """,
    "description": """
        An odoo Module to Manages Services  and Renewal relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_services", "mis_device_renewal"],
    "data": ["views/mis_device_renewal_views_inherit.xml"],
    "auto_install": True,
}
