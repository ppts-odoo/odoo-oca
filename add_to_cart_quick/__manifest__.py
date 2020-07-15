{
    'name'    : 'Add Bulk products to Cart',
    'version' : '12.0.1.0',
    'category': 'Website',
    'author'  : 'PPTS [India] Pvt.Ltd.',
    'website' : 'https://www.pptssolutions.com',
    'summary' : 'Add bulk products to website cart quickly',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'description': """
    Odoo E-Commerce
        Copy-Paste the product's name from shop page or reference number
        Which you would like to purchase the products
    """,
    'depends' : ['base', 'web', 'website','product', 'website_sale', 'stock'],
    'data': [
        'data/website_data.xml',
        'views/webiste_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
