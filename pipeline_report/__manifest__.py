# -*- coding: utf-8 -*-pipeline_reportres_users_view.xml
{
    'name': "Pipeline Report",

    'summary': """Pipeline Report""",

    'author': "PPTS [India] Pvt. Ltd.",
    'website': "http://www.pptssolutions.com",
    'category': '',
    'version': '0.1',
    'depends': ['base', 'crm','sales_team','website'],
    'data': [
        "security/pipeline_report_security.xml",
#         "security/base_groups.xml",
        "security/ir.model.access.csv",
        "wizard/pipeline_report_view.xml",
        "views/pipeline_view.xml",
        'views/report_web_template.xml',
        "views/res_users_view.xml"
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True
}
