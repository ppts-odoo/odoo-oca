# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Sales Tracking(Sales person wise)',
    'version': '10.0.1.1',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website' : 'http://www.pptssolutions.com',
    'category': 'sales',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends' : ['base','sale'],
    'description': """
           Sales Tracking sales person wise
    """,
    'data': [
        
        'views/custom_sale_view.xml',
        'data/sale_data.xml',
        'data/sale_mail_template.xml'
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application':True
}
