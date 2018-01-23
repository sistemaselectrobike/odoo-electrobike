# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Report',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Sales internal machinery',
    'description': """
This module contains all the common features of Sales Management and eCommerce.
    """,
    'depends': ['sale','pos_sale'],
    'data': [
        'report/sale_report.xml'
    ],
    'demo': [
        
    ],
    'uninstall_hook': "uninstall_hook",
    'css': [],
    'installable': True,
    'auto_install': False,
}