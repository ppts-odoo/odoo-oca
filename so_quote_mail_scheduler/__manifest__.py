# -*- coding: utf-8 -*-

{
    'name': 'Sale Quotation Mail Scheduler',
    'version': '12',
    'category': 'sale',
    'website': 'http://www.pptssolutions.com',
    'author': 'PPTS [India] Pvt. Ltd.',
    'depends': ['sale', 'sales_team', 'mail'],
    'data': [
        'security/base_groups.xml',
        'security/ir.model.access.csv',
        'data/mail_schedule_cron.xml',
        'views/sale_mail_schedule.xml',
        'wizards/sale_wizard.xml'
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
