# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name' : 'Work Order Multi User',
    'version': '12.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Manufacturing',
    'website':  'https://www.pptssolutions.com',
    'summary': 'More users in work order',
    'support': 'business@pptservices.com',
    'depends': [
        'mrp_workorder',
        'mrp'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/work_order_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
