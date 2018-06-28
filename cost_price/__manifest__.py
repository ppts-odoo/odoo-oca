# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Cost Price',
    'version': '10.0.2.0.0',
    'category': 'Sale',
    'depends': ['base','product','stock_account'],
    'author': 'PPTS,India',
    'website': 'www.pptssolutions.com',
    'data': [
        'security/cost_price_security.xml',
        'views/cost_price.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
