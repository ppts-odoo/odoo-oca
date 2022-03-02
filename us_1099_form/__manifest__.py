# -*- coding: utf-8 -*-
{
    'name': "Send 1099 form via mail",
    'summary': """Send 1099 form via mail""",
    'author': "PPTS [India] Pvt. Ltd.",
    'website': "http://www.pptssolutions.com",
    'category': 'Purchase,Account',
    'license': 'LGPL-3',
    'version': '11.0',
    'depends': ['base', 'mail','account','sale_management','purchase','web'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/account_wizard_view.xml",
        "wizard/vendor_wizard_view.xml",
        "views/res_partner_view.xml",
        "views/account_view.xml",
        "report/1099_form_report.xml",
        "report/1099_report_view.xml",
        "data/mail_template.xml",
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True
}
