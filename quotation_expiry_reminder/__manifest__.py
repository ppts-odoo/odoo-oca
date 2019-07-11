{
    'name': 'Quotation Expiry Reminder',
    'version': '12.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Sale',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'website': 'https://www.pptssolutions.com',
    'summary': 'Quotation Expiry Reminder for sale ',
    'description': """ Sale order Quotation Expiry Reminder
When user need to print the send mail sale order quotation  select the sale order list and
user need to click the "Quotation Expiry Reminder" in settings for generating the quotation expiry orders""",
    'summary': """This module will add a record to Quotation Expiry Reminder""",
    'depends': ['base','sale'],
    'data': [
        'data/sale_expiration_cron.xml',
        'data/expiration_mail_template_data.xml',
        'views/config_settings_inherit_view.xml',
    ],
'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    }


