# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Comparison Chart',
    'version': '13.0.0',
    'category': 'Purchase',
    'author':'PPTS [India] Pvt.Ltd.',
    'description': """
    Purchase Comparison Chart
    """,
    'license': 'LGPL-3',
    'summary': 'Purchase Comparison Chart',
    'depends': ['purchase','website', 'purchase_requisition'],
    'website': 'https://www.pptssolutions.com',
    'data': [
        'views/inherit_purchase_requisition_view.xml',
        'views/bid_templates.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
}
