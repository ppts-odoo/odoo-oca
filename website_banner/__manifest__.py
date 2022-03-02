# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dynamic Website Banner',
    'category': 'Website',
    'sequence': 140,
    'summary': 'Website Banner',
    'website': 'http://www.pptssolutions.com',
    'author': 'PPTS [India] Pvt.Ltd.',
    'version': '10.1',
    'description': """
        Adding time based banner to the website
        """,
    'depends': ['website_sale','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_banner.xml',
        'views/website_banner_templates.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
