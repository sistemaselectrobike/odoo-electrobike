# -*- coding: utf-8 -*-
{
    'name': "Extension for accounting module",

    'summary': """
        This module modifies the invoice report""",

    'description': """
        Adds extra fields to the invoice report so it generates the requested data
    """,

    'author': "Electrobike",
    'website': "http://www.electrobike.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
