# -*- coding: utf-8 -*-
{
    'name': 'Drop Shipping Extended',
    'version': '1.0',
    'category': 'Sale Management',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
     'license': 'LGPL-3',
    'description':"""
                This module allows the System to route drop shipping in sale order line item.
        """,
    'depends': ['base','sale','purchase',"stock"],
    'data': [
#             'security/ir.model.access.csv',
            'view/stock_picking_view.xml',
            'view/delivery_order_view.xml',
            'view/purchase_order_views.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}