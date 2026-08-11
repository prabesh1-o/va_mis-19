{
    "name": "MIS Customer Portal",
    "summary": """
         MIS Module to Manage Customer Portal
        """,
    "description": """
         An odoo module for MIS to Manage Customer Portal
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["va_mis", "mis_device", "mis_tickets", "mis_vehicle", "portal"],
    "data": [
        "views/res_config_settings.xml",
        "views/device_portal_templates.xml",
        "views/ticket_portal_templates.xml",
        "views/customer_portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "mis_customer_portal/static/src/select2.min.css",
            "mis_customer_portal/static/src/select2.min.js",
            "mis_customer_portal/static/src/select2.js",
            "mis_customer_portal/static/src/js/customer_portal.js"
        ],
        "web.assets_backend": ["mis_customer_portal/static/src/js/customer_portal.js",],
    },
    "installable": True,
    "application": True,
}
