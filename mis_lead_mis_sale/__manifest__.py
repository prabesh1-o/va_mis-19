{
    "name": "Raw Lead MIS Sales",
    "summary": """
        Manages Services  and sales relationship
        """,
    "description": """
        An odoo Module to Manages Services  and sales relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_lead", "mis_sale"],
    "data": [
        "views/sale_order_views_inherit.xml",
        "views/mis_raw_lead_views_inherit.xml",
    ],
    "auto_install": True,
}
