# -*- coding: utf-8 -*-
{
    'name': 'Bulk Products Publish',
    'version': '12.00',
    'sequence' : 0,
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description':"""
                Publishing/Unpublishing bulk products on website
                      """,
    'depends': ['base','product','sale','website_sale', 'website_mail','decimal_precision','mail','sale_management'],
    'data': [    
                'wizard/product_publish_wizard_view.xml',      
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
