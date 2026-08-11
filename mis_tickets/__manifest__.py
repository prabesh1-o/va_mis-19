{
    "name": "MIS Tickets",
    "summary": """
        Manages Tickets for complaints
        """,
    "description": """
        An odoo Module to Manage MIS Complaints and Tickets
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mail", "mis_device"],
    "data": [
        "security/ticket_security.xml",
        "security/ticket_menu_security.xml",
        "security/ticket_record_rule.xml",
        "security/ir.model.access.csv",
        "data/cron_completed_tickets.xml",
        "data/ticket_completed.xml",
        "views/mis_ticket_menu_views.xml",
        "views/res_partner_inherit.xml",
        "views/mis_ticket_views.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mis_tickets/static/src/**/**/*.js",
            "mis_tickets/static/src/**/**/*.xml",
        ],
    },
    "installable": True,
    "application": True,
}
