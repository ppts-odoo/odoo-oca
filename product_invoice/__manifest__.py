{
    'name' : 'Product Invoice',
    'version' : '1.1',
    'summary': 'Product Invoicing',
    'sequence': 1,
    'description': """Calculating the total amount invoiced""",
    'category': 'Product',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'images' : [],
      'depends': [
        'account',
        'product',
        'sale',
    ],
    'data': [
        'views/product_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}