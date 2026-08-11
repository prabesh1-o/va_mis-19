{
    "name": "MIS Reseller",
    "summary": """
        Manages Mis Reseller flow
        """,
    "description": """
        An odoo Module to Manage reseller data from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": [
        "mis_customer",
        "mis_installation_sale_service",
        "mis_inventory_mis_device",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/reseller_menuitem.xml",
        "views/sale_order_inherit.xml",
        "views/mis_inventory_device_inherit.xml",
        "views/sales_order_views.xml",
    ],
    "installable": True,
    "application": True,
}
