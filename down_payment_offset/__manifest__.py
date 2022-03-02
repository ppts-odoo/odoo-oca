# -*- encoding: utf-8 -*-
{
    'name': 'Down Payment Offset',
    'version': '12.0',
    'category': 'sale',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'Adjust your down payment',
    'description': """
    This module adds additional features while create down payment 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base','sale','sale_down_payment'],
    'data': [
        'wizard/create_invoice.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
}
