# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dynamic Website Banner',
    'category': 'Website',
    'sequence': 140,
    'website': 'http://www.pptssolutions.com',
    'summary': 'Website,Banner',
    'version': '11.0',
    'author' : 'PPTS India Pvt Ltd',
    'description': """
        Adding time based website banner
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
