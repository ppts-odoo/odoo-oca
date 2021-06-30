# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SO and MO Reference',
    'version': '13.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'MRP',
    'sequence': 5,
    'license': 'LGPL-3',
    'summary': 'This module is based on sale order sequence is reference to manufacturing and work order process.',
    'description': """
    This module enables the  sale sequence is reference for manufacturing order and work order process using the
     so reference we can filter the manufacture order and work order details for which sale order against we can
     easily identify the order.
""",
    'website': 'https://www.pptssolutions.com',
    'depends': [
        'base','mrp','sale','stock'
    ],
    'data': [
        'views/mrp_view.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
