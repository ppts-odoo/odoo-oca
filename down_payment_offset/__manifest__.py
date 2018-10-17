# -*- encoding: utf-8 -*-
{
    'name': 'Down Payment Offset',
    'version': '10.0',
    'category': 'sale',
    'description': """
    This module adds additional features while create down payment 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'Adjust down payments',
    'depends': ['base','sale','stock','sale_down_payment'],
    'data': [
        'wizard/create_invoice.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
