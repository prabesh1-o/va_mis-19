{
    "name": "Raw Lead MIS Services",
    "summary": """
        Manages Services  and Raw Lead relationship
        """,
    "description": """
        An odoo Module to Manages Services  and Renewal relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_lead", "mis_services"],
    "data": [
        "security/ir.model.access.csv",
        "views/mis_raw_lead_views_inherit.xml",
    ],
    "auto_install": True,
}
