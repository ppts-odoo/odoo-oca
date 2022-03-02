# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quotations/Sales Orders Approval',
    'version': '14.0',
    'category': 'Sales',
    'author': 'PPTS',
    'sequence': 15,
    'summary': 'Quotations/Sales Orders Approval',
    'description': """
Manage sales quotations and orders Approval.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends': ['base', 'base_setup','sale_management', 'sales_team', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'wizard/sale_approval_reason_view.xml',
        'views/res_user_views.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
}
