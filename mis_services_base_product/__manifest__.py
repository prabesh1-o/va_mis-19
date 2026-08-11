{
    "name": "MIS Services Product",
    "summary": """
        Manages Services  and Product relationship
        """,
    "description": """
        An odoo Module to Manages Services  and Product relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_services", "product"],
    "data": ["views/product_template_inherit.xml", "views/mis_services_inherit.xml",],
    "auto_install": True,
}
