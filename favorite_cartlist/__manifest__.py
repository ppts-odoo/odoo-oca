# -*- coding: utf-8 -*-

{
    'name' : 'Favorite Cart List in E-Commerce',
    'version' : '1.0',
    'author' : 'PPTS [India] Pvt.Ltd.',
    'sequence': 1,
    'category': 'e-commerce',
    'website' : 'http://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'This module adds the products from cart to a separate list called favorites.',
    'description' : """ This Module is to add the favorite products to a separate section like wishlist and checkouts with the added favorite products.
    """,
    'depends' : ['base', 'sale', 'website','website_sale'],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/favorites_cart.xml',
        'views/favorites.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable' : True,
    'application' : True,
}
