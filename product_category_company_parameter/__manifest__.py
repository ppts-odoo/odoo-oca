# -*- coding: utf-8 -*-
{
    'name' : 'Product Category Company Parameter',
    'version' : '13.0',
    'sequence': 0,
    'category' : 'Product',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'support': 'business@pptservices.com',
    'depends': ['product','base','account', 'account_asset','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_company_categ_view.xml',
        #'views/product_category_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
