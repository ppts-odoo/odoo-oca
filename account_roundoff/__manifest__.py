{
    'name' : 'Round Off value',
    'version' : '1.0',
    'author' : 'PPTS [India] Pvt.Ltd.',
    'sequence': 110,
    'category': 'Account',
    'website' : 'http://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description' : """ This module manage value round-off on the total amount of Quotation, Purchase Order and Invoice (Sales& Purchase).
        After installing this module, on Settings -> Configuration -> Accounting a field is enabled for default Round Off account. This should be mapped to get the rounded value hit on financial books.
    """,
    'depends' : ['base', 'account', 'sale', 'purchase'],
    'data' : [
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_config_view.xml',
    ],
    'images': ['static/description/banner.png'], 
    'installable' : True,
    'application' : True,
}
