{
    'name': 'Odoo 19 Budget Management',
    'version': '19.0.1.0.0',
    'summary': 'Budget Management for Odoo 19 Community Edition',
    'description': """
Budget Management for Odoo 19 Community Edition.

This module allows accountants to manage analytic accounts and budgets.
""",
    'category': 'Accounting',
    'author': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
    ],

    'images': ['static/description/banner.png'],

    'installable': True,
    'application': False,
    'auto_install': False,
}