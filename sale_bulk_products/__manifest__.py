# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'SO Line Bulk products Add',
    'version': '11.0.0.0.0',
    'category': 'Sale',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends': ['base', 'sale','product','stock'],
    'author': 'PPTS [India] Pvt.Ltd.',
    'summary': 'Multiple Products in line item',
    'description': 'Used to select bulk products to confirm sale.',
    'website': 'https://www.pptssolutions.com',
    'data': [
        'views/sale_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
