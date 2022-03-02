# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase/Quotation Mass Mailing',
    'version': '12.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Purchase',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'Send Purchase/Quotation By Mail',
    'description': """
It helps, when user select the records and by triggering the action server menu (Send Purchase/Quote by Mail), It opens a wizard view and by clicking the Send Mail button the selected records will receive an email.
""",
    'website': 'www.pptssolution.com',
    'depends': ['base','purchase'],
    'data': [
        'wizard/po_bulk_mail.xml',
        'views/purchase_action_menu.xml',  
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
