# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Name',
    'category': 'Website',
    'website': 'https://www.pptssolutions.com/',
    'author': 'PPTS India Pvt Ltd',
    'summary': 'Website Product Name',
    'version': '1.1',
    'description': """
    Website Product Name
        """,
    'depends': ['website_sale', 'product','website'],
    'data': [
        'views/website_template.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': True,
}
