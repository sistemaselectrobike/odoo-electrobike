# -*- coding: utf-8 -*-
{
    'name': "Electrobike sale stock enhancement",

    'summary': """Electrobike sale stock enhancement""",

    'description': """
Electrobike sale stock enhancement
==================================
""",

    'author': "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Sales',
    'version': '1',
    'depends': ['sale_stock'],
    'data': [
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
}
