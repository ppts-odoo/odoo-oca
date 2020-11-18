# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Lines',
    'version': '12.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'category': 'sale',
    'description': """Enhancement in sale module""",
    'depends': ['base','sale_management','sale'],
    'license': 'LGPL-3',
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
