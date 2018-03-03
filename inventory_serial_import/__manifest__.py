# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Serial Number Import',
    'version': '1.1',
    'website' : 'http://www.pptssolutions.com',
    'category': 'inventory',
    'depends' : ['base','stock'],
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description': """
           Serial Number Import
    """,
    'data': [
        
        'views/inventory_serial_import_view.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application':True
}
