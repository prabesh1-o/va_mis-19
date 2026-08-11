{
    "name": "MIS Sale",
    "summary": """
        Manages Mis Sales
        """,
    "description": """
        An odoo Module to Manage Sales from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["base", "mail", "sale", "mis_services","mis_services_base_product"],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_order_group.xml",
        "wizard/sale_wizard.xml",
        "views/sale_view_inherit.xml",
        "views/invoiced_sale_order.xml",
        "views/mis_services_inherit.xml",
        "views/sales_menuitem.xml",
    ],
    "installable": True,
    "application": True,
}
