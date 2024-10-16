# -*- coding: utf-8 -*-
{
    'name': 'Global Product Search on website',
    'version': '10.0.1.0',
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description':"""
                Custom Sale purchase product management
        """,
    'depends': ['base','product','sale','website_sale', 'website_mail'],
    'data': [
               'views/product_web_custom.xml',
               'views/advance_search.xml',         
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
