{
    "name": "MIS Requirement Collection",
    "summary": """
        MIS Requirement Collection from Employees
        """,
    "description": """
        An odoo Module to manage requirement collections
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["base", "mail", "va_mis"],
    "license": "LGPL-3",
    "data": [
        "security/requirements_security.xml",
        "security/ir.model.access.csv",
        "views/requirements.xml",
    ],
    "installable": True,
    "application": True,
}
