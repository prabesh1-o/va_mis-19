{
    "name": "MIS Timesheet",
    "summary": """
        Manages MIS Timesheets
        """,
    "description": """
        An odoo Module to Manage Timesheets
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "va_mis", "hr_timesheet"],
    "data": ["views/hr_timesheet_inherit.xml",],
    "installable": True,
    "application": True,
}
