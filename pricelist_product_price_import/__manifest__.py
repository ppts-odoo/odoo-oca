# -*- coding: utf-8 -*-
{
    'name': 'Pricelist Product Price Import',
    'summary': ' This module allows you to import products to line items based on product category.',
    'version': '11',
    'category': 'sale',
    'description': """
       Configuration:
       In Import Product Category model a  button called import is added in product pricelist.
       When we click import button products under the product category is added to line items.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'product', 'sale', 'sale_management'],
    'data': [
        
        'views/import_products_view.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application':True,
    'active': False,
}


