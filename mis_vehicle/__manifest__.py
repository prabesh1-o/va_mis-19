{
    "name": "mis_vehicle",
    "summary": """ Vehicle's module in FLeet Management System by Vitruvian Analytica. """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "MIS",
    "version":  '19.0.1.0.0',
    "depends": ["base", "mail", "va_mis", "mis_device"],
    "data": [
        "security/mis_vehicle_security.xml",
        "security/ir.model.access.csv",
        "security/mis_vehicle_rule.xml",
        "views/mis_vehicle_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
