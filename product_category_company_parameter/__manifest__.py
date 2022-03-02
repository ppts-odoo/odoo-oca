# -*- coding: utf-8 -*-
{
    'name' : 'Product Category Company Parameter',
    'version' : '12.0',
    'sequence': 0,
    'category' : 'Product',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'support': 'business@pptservices.com',
    'depends': ['product','base','account', 'account_asset','stock'],
    'data': [
        'wizard/wizard_company_categ_view.xml',
        'views/product_category_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
