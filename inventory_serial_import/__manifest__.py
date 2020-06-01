# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import Serial Numbers on Delivery Orders',
    'version': '1.1',
    'author': "PPTS India Pvt Ltd",
    'website': 'https://www.pptssolutions.com',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends' : ['base','stock'],
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
