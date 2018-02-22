# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Serial Number Import',
    'version': '1.1',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website' : 'http://www.pptssolutions.com',
    'category': 'Warehouse',
    'depends' : ['base','stock'],
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
