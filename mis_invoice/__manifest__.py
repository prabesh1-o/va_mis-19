{
    "name": "MIS Invoice",
    "summary": """
        Manages Mis Invoices
        """,
    "description": """
        An odoo Module to Manage Invoices from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "account", "va_mis"],
    "data": [
        "security/invoice_security.xml",
        "security/invoice_record_rule.xml",
        "security/ir.model.access.csv",
        "data/automate_npa_status.xml",
        "views/invoice_menuitem.xml",
        "views/res_config_settings.xml",
        "views/account_move_inherit.xml",
    ],
    "installable": True,
    "application": True,
}
