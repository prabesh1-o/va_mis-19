{
    "name": "MIS Product Stock",
    "summary": """
        Manages Product  and Stock relationship
        """,
    "description": """
        An odoo Module to Manages Product  and Stock for buttons
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_products", "stock", "mis_purchase"],
    "data": ["views/mis_product_inherit.xml"],
    "auto_install": True,
}
