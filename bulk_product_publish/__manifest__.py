# -*- coding: utf-8 -*-
{
    'name': 'Bulk Products Publish',
    'version': '15.00',
    'sequence' : 0,
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description':"""
                Publishing/Unpublishing bulk products on website
                      """,
    'depends': ['base','product','sale','website_sale'],
    'data': [    
                'security/base_groups.xml',
                'security/ir.model.access.csv',
                'wizard/product_publish_wizard_view.xml',      
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
