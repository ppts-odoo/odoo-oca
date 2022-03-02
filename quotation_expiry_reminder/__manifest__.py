{
    'name': 'Quotation Expiry Reminder',
    'summary': """This module will add a record to Quotation Expiry Reminder""",
    'version': '10.0.1.0.0',
    'description': """
    
Manage sales Quotation Expiry Reminder 
======================================

This application allows you to manage your sales goals in an effective and efficient manner by keeping track of all sales orders and expiration details.

It handles the full Quotation Expiry Reminder:

* **Quotation** -> **Sales order** -> **Quotation**

You can choose flexible Expiration date methods:
------------------------------------------------

* *One week before*
* *Two weeks before*
* *One month before*

With this module you can personalize the sale order and Quotation Expiry Reminder with
expiry date. Automatically send mail to user from the Salesperson. 

    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Sale',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends': ['sale'],
    'data': [
        'data/sale_expiration_cron.xml',
        'data/expiration_mail_template_data.xml',
        'views/config_settings_inherit_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    }
