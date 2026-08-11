{
    "name": "MIS Installation Sale Service",
    "summary": """
        Manages Mis Sales , Services and Installation
        """,
    "description": """
        An odoo Module to Manage Sales, Installation and Service from MIS
    """,
    "author": "Vitruvian Analytica",
    "website": "https://github.com/prashant1gh/fleet-management",
    "category": "Uncategorized",
    "version":  '19.0.1.0.0',
    "license": "LGPL-3",
    "depends": ["mis_installation_mis_sales", "mis_services"],
    "data": ["views/sale_view_inherit.xml",],
    "installable": True,
    "application": True,
}
