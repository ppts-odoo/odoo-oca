# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Canned Response',
    'website': 'https://www.pptssolutions.com/',
    'author': 'PPTS [India] Pvt.Ltd.',
    'summary': 'Canned Response',
    'version': '12.0.1.1',
    'license': 'LGPL-3',
    'description': """
    Canned Response
        """,
    'depends': ['mail','base'],
    'data': [
        'views/canned_response.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
