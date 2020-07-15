{
    'name'    : 'Add Bulk products to Cart',
    'version' : '10.0.1.0',
    'category': 'Website',
    'author'  : 'PPTS [India] Pvt.Ltd.',
    'website' : 'https://www.pptssolutions.com',
    'summary' : 'Add bulk products to website cart quickly',
    'author'  : 'PPTS [India] Pvt.Ltd.',
    'website' : 'http://www.pptssolutions.com',
    'description': """
    Odoo E-Commerce
        Copy-Paste the product's name from shop page or reference number
        Which you would like to purchase the products
    """,
    'depends' : ['base', 'web', 'website','product', 'website_sale'],
    'data': [
        'data/website_data.xml',
        'views/webiste_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',	
}
