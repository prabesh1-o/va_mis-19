{
    "name": "MIS Bulk Payment",
    "summary": """
        Manages Bulk Payments received from Customer
        """,
    "description": """
        An odoo Module to Manage and track the Bulk Payments received from Customer
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "depends": ["mail", "mis_invoice"],
    "data": [
        "security/bulk_payment_security.xml",
        "security/ir.model.access.csv",
        "views/bulk_payment.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
