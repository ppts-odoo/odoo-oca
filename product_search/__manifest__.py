# -*- coding: utf-8 -*-
{
    'name': 'Product Global Search on website',
    'version': '12.0',
    'sequence':0,
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description':"""
                Product Global Search
        """,
    'depends': ['base','product','sale','website_sale','website_mail','sale_management'],
    'assets': {
        'web.assets_frontend': [
            'product_search/static/src/js/custom.js',
        ],
    },
    'data': [
               # 'views/product_web_custom.xml',
               'views/advance_search.xml',         
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
