# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Serial Number Import on Production',
    'version': '12.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website' : 'http://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'category': 'Manufacturing',
    'depends' : ['base','mrp','stock'],
    'description': """
          Import serial numbers from 'csv' file on clicking produce button.
    """,
    'data': [
        
        'views/production_serial_import_view.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application':True
}
