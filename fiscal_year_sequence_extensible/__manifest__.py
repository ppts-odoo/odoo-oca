# -*- coding: utf-8 -*-
{
    'name': "Fiscal Year Sequence Extensible",

    'summary': """
        Fiscal Year Sequence Extensible""",

    'description': """
        Fiscal year sequence extensible module is to add prefix and suffix from date range of sequence. We can use %(prefix)s and %('suffix')s as prefix and suffix code.
    """,

    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    "complexity": "easy",
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    # for the full list
    'category': 'Account',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_sequence_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}
