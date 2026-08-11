{
    "name": "MIS Carousel Manager",
    "summary": """
        MIS Carousel Manager
        """,
    "description": """
        An odoo Module to Manage carousel in mobile app ,
        it provides an api for the content and image management
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["base", "mail", "va_mis"],
    "license": "LGPL-3",
    "data": ["security/ir.model.access.csv", "views/carousel_manager_views.xml",],
    "installable": True,
    "application": True,
}
