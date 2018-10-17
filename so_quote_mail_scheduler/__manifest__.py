# -*- coding: utf-8 -*-

{
    'name' : 'Sale Quotation Mail Scheduler',
    'version' : '10',
    'summary': ' ',
    'description': """Sale Quotation Mail Scheduler""",
    'category': 'sale',
    'website': 'http://www.pptssolutions.com',
    'author':'PPTS',
    'depends' : ['sale','sales_team','mail'],
    'data': [ 
        'data/mail_schedule_cron.xml',
        'views/sale_mail_schedule.xml',
        'wizards/sale_wizard.xml'
        ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
