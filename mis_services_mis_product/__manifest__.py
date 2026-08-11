{
    "name": "MIS Services MIS Product",
    "summary": """
        Manages Services  and MIS Product relationship
        """,
    "description": """
        An odoo Module to Manages Services  and MIS Product relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_services", "mis_products"],
    "data": ["views/mis_service_views_inherit.xml", "views/mis_products_menuitem.xml",],
    "auto_install": True,
}
