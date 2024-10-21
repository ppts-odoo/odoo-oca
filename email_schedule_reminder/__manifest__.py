
{
    'name': 'Month End Email Scheduler',
    'version': '15.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'General',
    'license': 'LGPL-3',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base','mail'],
    'description': """ 
    This module will generate emails based on the selected templates at every month end.""",
    'data': [
        'security/ir.model.access.csv',
        'data/email_reminder_cron.xml',
        'views/email_scheduler_view.xml',
        'views/email_scheduler_menu_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}


