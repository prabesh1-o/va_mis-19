{
    "name": "MIS Product Base Product",
    "summary": """
        Manages Product  and Base Product relationship
        """,
    "description": """
        An odoo Module to Manages Product  and Base Product relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_products", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/mis_product_inherit.xml",
        "views/product_template_inherit.xml",
    ],
    "auto_install": True,
}
