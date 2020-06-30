# -*- encoding: utf-8 -*-
{
    'name': 'Sales Advanced Downpay',
    'version': '12.0',
    'license': 'LGPL-3',
    'category': 'sale',
    'description': """
    This module adds additional features while create down payment 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'support': 'business@pptservices.com',
    'summary': 'Additional features in down payment',
    'depends': ['base','sale'],
    'data': [
        'wizard/sale_make_invoice_advance_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
}
