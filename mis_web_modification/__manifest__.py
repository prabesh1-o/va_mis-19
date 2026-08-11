{
    "name": "MIS Website Modification",
    "summary": """
        Manages Mis Website Modification
        """,
    "description": """
        An odoo Module to Manage Website Modification
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "va_mis", "website_sale"],
    "data": ["views/website_shop_inherit.xml"],
    "assets": {
        "web.assets_backend": [
            "va_mis/static/src/js/*.js",
            "va_mis/static/src/css/*.scss",
        ]
    },
    "installable": True,
    "application": True,
}
