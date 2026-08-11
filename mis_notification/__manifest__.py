{
    "name": "mis_notification",
    "summary": """ Notification module in  MIS System by Vitruvian Analytica. """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Fleet Management",
    "license": "AGPL-3",
    # any module necessary for this one to work correctly
    # always loaded
    "depends": ["web", "bus", "base", "mail"],
    "data": [
        # "security/ir.model.access.csv",
        # "views/res_users_demo.xml",
    ],
    "assets": {
        "web.assets_backend": ["mis_notification/static/src/js/services/*.js",]
    },
    "installable": True,
    "application": True,
}
