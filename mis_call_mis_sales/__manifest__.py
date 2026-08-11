{
    "name": "MIS Call MIS Sales",
    "summary": """
        Manages call and sales relationship
        """,
    "description": """
        An odoo Module to Manage Call  and Sales relationship
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_call", "mis_sale"],
    "data": ["views/mis_call.xml", "security/ir.model.access.csv"],
    "auto_install": True,
}
