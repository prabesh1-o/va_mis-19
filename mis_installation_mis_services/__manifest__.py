{
    "name": "MIS Installation  MIS Services",
    "summary": """
        Manages Installation  and Services relationship
        """,
    "description": """
        An odoo Module to Manages Installation  and Services relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_installation_mis_device", "mis_services"],
    "data": ["views/installation_view_inherit.xml", "views/mis_services_inherit.xml",],
    "auto_install": True,
}
