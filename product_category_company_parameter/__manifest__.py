# -*- coding: utf-8 -*-
{
    'name' : 'Product Category Company Parameter',
    'version' : '1.1',
    'category' : 'Product',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends': ['product','base','account', 'account_asset'],
    'data': [
        'wizard/wizard_company_categ_view.xml',
        'views/product_category_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
