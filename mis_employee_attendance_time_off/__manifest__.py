{
    "name": "MIS Employee Attendance Time Off",
    "summary": """
        Manages Employees, Attendance and Time Off
        """,
    "description": """
        An odoo Module to Manage Employees, Attendance and Time Off
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_employee", "mis_attendance", "mis_time_off"],
    "data": ["views/hr_menuitems.xml",],
    "auto_install": True,
}
