# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import Serial Numbers on Delivery Orders',
    'version': '1.1',
    'website' : 'http://www.pptssolutions.com',
    'author' : 'PPTS [India] Pvt. Ltd.',
    'category': 'inventory',
    'depends' : ['base','stock'],
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description': """
           Product Serial Numbers Import on Delivery Orders
    """,
    'data': [
        
        'views/inventory_serial_import_view.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application':True
}
