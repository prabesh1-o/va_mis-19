{
    "name": "MIS Service Components",
    "summary": """
        Manages MIS Service Components
        """,
    "description": """
        An odoo Module for audit firm.
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mis_services"],
    "data": ["security/ir.model.access.csv", "views/service_component.xml"],
    "installable": True,
    "application": True,
}
