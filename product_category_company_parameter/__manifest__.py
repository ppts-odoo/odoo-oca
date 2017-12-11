# -*- coding: utf-8 -*-
{
    'name' : 'Product Category Company Parameter',
    'version' : '1.1',
    'category' : 'Product',
    'author' : 'PPTS',
    'website': 'http://www.pptssolutions.com',
    'depends': ['product','base','account', 'account_asset'],
    'data': [
        'wizard/wizard_company_categ_view.xml',
        'views/product_category_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
