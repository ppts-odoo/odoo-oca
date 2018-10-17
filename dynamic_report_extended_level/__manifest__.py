# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Dynamic Report Extended',
    'category': 'Accounting',
    'summary': 'Balance Sheet report extended',
    'author': 'PPTS [India] Pvt.Ltd.',
    "website": "http://www.pptssolutions.com",
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description': """
This module help to view financial report of grand children data
=========================
        """,
    'depends': ['account_reports'],
    'data': ['views/report_financial.xml'
    ],
    'images': ['static/description/banner.png'],
    "auto_install": False,
    "installable": True,
    "application": False,
}
