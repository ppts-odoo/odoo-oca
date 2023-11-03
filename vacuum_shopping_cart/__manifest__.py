# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Clear Shopping Carts',
    'version' : '16.0.1',
    'summary': 'Clear Shopping Carts',
    'sequence': 30,
    'website': 'http://www.pptssolutions.com',
    'author':'PPTS [India] Pvt. Ltd.',
    'description': """
        Clear your shopping cart with a single click in Website Shop.
    """,
    'category': 'Website',
    'depends' : ['base', 'web','base_setup', 'sale', 'website_sale','website'],
    'data': [
        'views/website_sale_extends.xml',
        'views/templates.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
