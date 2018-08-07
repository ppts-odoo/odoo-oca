# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Custom Sale Mass Mailing',
    'version': '10.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Sale',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'summary': 'Send SO/Quotation By Mail',
    'description': """
It helps, when user select the records and by triggering the action server menu (Send SO/Quote by Mail), It opens a wizard view and by clicking the Send Mail button the selected records will receive an email.
""",
    'website': 'www.pptssolution.com',
    'depends': ['base','sale'],
    'data': [
        
        'wizard/so_bulk_mail.xml',
        'views/sale_action_menu.xml',  
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}