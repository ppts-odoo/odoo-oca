# -*- coding: utf-8 -*-
{
    'name': 'Bulk Products Publish',
    'version': '1.1',
    'sequence' : 0,
    'category': 'Website',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'description':"""
                Publishing/Unpublishing bulk products  
                      """,
    'depends': ['base','product','sale','website_sale', 'website_mail','decimal_precision','mail','sale_management'],
    'data': [    
                'wizard/product_publish_wizard_view.xml',      
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}