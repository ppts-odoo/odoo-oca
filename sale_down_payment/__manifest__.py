# -*- encoding: utf-8 -*-
{
    'name': 'Sales Advanced Downpay',
    'version': '10.0',
    'category': 'sale',
    'description': """
    This module adds additional features while create downpayment 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'Additional features in down payment',
    'depends': ['base','sale'],
    'data': [
        'wizard/sale_make_invoice_advance_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/banner.png'],
}
