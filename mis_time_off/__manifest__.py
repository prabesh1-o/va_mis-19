{
    "name": "MIS Time Off",
    "summary": """
        Manages Mis Time off
        """,
    "description": """
        An odoo Module to Manage Time Off from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "hr_holidays", "va_mis"],
    "data": ["views/time_off_views.xml",],
    "installable": True,
    "application": True,
}
