{
    "name": "mis_nepali_date_widget",
    "summary": """ Nepali Date Widget module in  MIS System by Vitruvian Analytica. """,
    "description": """
        Long description of module's purpose
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Fleet Management",
    "license": "AGPL-3",
    # any module necessary for this one to work correctly
    # always loaded
    "depends": ["base"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "mis_nepali_date/static/src/**/**/*.xml",
            "mis_nepali_date/static/src/components/nepali_date_picker/*.js",
        ]
    },
    "installable": True,
    "application": True,
}
