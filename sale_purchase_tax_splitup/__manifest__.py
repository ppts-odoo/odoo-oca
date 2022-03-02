# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales and Purchase Tax Split-up',
    'version': '12',
    'category': 'Sales/Purchase',
    'sequence': 0,
    'website': "http://www.pptssolutions.com",
    'summary': 'Sales/Purchase Tax Split-up',
    'description': """
Manage Sales/Purchase Tax Split-up
==================================

This application allows you to manage your "Sales/Purchase Tax Split-up".

    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'depends': ['sale','sale_management', 'purchase', 'account'],
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'data': [
        'security/base_groups.xml',
       'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/purchase_views.xml',
      
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
}
