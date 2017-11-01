# -*- coding: utf-8 -*-
{
    'name': 'Product Global Search',
    'version': '1.0',
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'description':"""
                Product Global Search
        """,
    'depends': ['base','product','sale','website_sale', 'website_mail'],
    'data': [
               'views/product_web_custom.xml',
               'views/advance_search.xml',         
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}