{
    "name": "MIS Module",
    "summary": """
        Manages Tracmate users and devices
        """,
    "description": """
        An odoo Module to Manage Tracmate users and devices
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "web", "spreadsheet", "hr"],
    "data": [
        "security/mis_action_security.xml",
        "security/mis_security.xml",
        "security/fiscal_period_security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
        "views/res_partner_menu_action.xml",
        "views/res_partner_views_inherit.xml",
        "views/mis_note_template.xml",
        "views/mis_fiscal_period.xml",
        "views/res_company.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "va_mis/static/src/js/custom_date_filter/*.js",
            "va_mis/static/src/js/*.js",
            "va_mis/static/src/css/sticky.scss",
        ]
    },
    "installable": True,
    "application": True,
}