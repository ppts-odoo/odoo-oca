{
    'name': 'Product Invoice',
    'version': '15',
    'summary': 'Product Invoicing',
    'sequence': 1,
    'description': """Calculating the total amount invoiced""",
    'category': 'Product',
    'author': 'PPTS [India] Pvt.Ltd.',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'website': 'https://www.pptssolutions.com',
    'images': [],
    'depends': [ 'account', 'product', 'sale',
    ],
    'data': [
        'views/product_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
