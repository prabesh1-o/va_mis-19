{
    "name": "MIS Employee",
    "summary": """
        Manages Mis Employees
        """,
    "description": """
        An odoo Module to Manage Employees from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["va_mis", "hr"],
    "data": ["views/mis_employee_view.xml",],
    "installable": True,
    "application": True,
}
