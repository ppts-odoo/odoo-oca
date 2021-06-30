# -*- coding: utf-8 -*-

{
    'name': 'Purchase Order Lines',
    'version': '13.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'category': 'Purchase',
    'description': """Enhancement in Purchase module""",
    'depends': ['base','purchase'],
    'license': 'LGPL-3',
    'data': [
        'views/purchase_order_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
