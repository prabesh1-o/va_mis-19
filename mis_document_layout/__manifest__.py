{
    "name": "MIS Document Layout",
    "summary": """
        Manages Mis Document Layout
        """,
    "description": """
        An odoo Module to Manage Sales from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mail", "sale", "account"],
    "data": [
        "reports/sale_report_template.xml",
        "reports/invoice_report_template.xml",
        "views/mis_document_layout.xml",
        "data/report_layout.xml",
    ],
    "installable": True,
    "application": True,
}
