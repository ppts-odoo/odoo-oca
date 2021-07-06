{
    'name': 'Reorder Quantity Mail Notification',
    'version': '13.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'website': 'https://www.pptssolutions.com',
    'summary': 'Reorder Quantity mail notification for Purchase',
    'description': """ Reorder Quantity mail notification """,
    'depends': ['base','purchase'],

    'data': [
        'data/reorder_qty_mail_template.xml',
        'data/reorder_qty_mail_notification_cron.xml',
        'views/config_settings_inherit_view.xml',
        'views/reorder_qty_notification_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/banner.png'],
    }

