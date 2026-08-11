{
    "name": "MIS Device",
    "summary": """
        Manages Tracmate users and devices
        """,
    "description": """
        An odoo Module to Manage Tracmate users and devices
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version": "19.0.1.0.0",
    "depends": ["base", "mail", "va_mis","account"],
    "license": "LGPL-3",
    "data": [
        "security/device_security.xml",
        "security/sim_security.xml",
        "security/access_rules.xml",
        "security/ir.model.access.csv",
        "data/cron_expired_devices.xml",
        "data/cron_sim_recharge.xml",
        "views/mis_device_views.xml",
        "views/device_sims_views.xml",
        "views/res_partner_views_inherit.xml",
        "views/mis_device_sim_recharge_views.xml",
        "views/mis_device_sim_recharge_history_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
}
