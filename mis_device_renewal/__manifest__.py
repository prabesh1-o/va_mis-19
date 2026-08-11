{
    "name": "MIS Device Renewal Module",
    "summary": """
         MIS Module to Manage Renewal
        """,
    "description": """
         An odoo module for MIS to Manage Renewal
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mis_device", "account"],
    "data": [
        "security/renewal_security.xml",
        "security/renewal_record_rule.xml",
        "reports/renewal_pi_template.xml",
        "reports/ir_actions_report.xml",
        "wizard/renewal_wizard.xml",
        "security/ir.model.access.csv",
        "data/cron_expired_device.xml",
        "data/renewal_stages.xml",
        "data/renewal_mail_template_data.xml",
        "views/renewal_views.xml",
        "views/inactive_renewal_views.xml",
        "views/mis_invoice_inherit_views.xml",
        "views/device_inherit_views.xml",
        "views/device_renewal_history_views.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "application": True,
}
