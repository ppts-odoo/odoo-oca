# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sales Amendment',
    'version' : '1.1',
    'summary': 'Sales Amendment',
    'sequence': 1,
    'description': """ Sales Order Amendment
When user need to modify/amend a product/quantity/price in a confirmed sale order, user should not modify it in the sale order directly. The sale order represents what the customer really ordered. The changes would not be repercuted on the delivery order and invoices neither.
But this module allows the user can do modify / amend on confirmed  orders. Once user click on the "Amendment" button, then this will create the same order in editable mode, with the same base number and a '-XXX' suffix appended. A message is added in the chatter saying that a new revision was created.
In the form view, a new tab is added that lists the previous revisions, with the date they were made obsolete and the user who performed the action.
The old revisions/amendments of a sale order are flagged as inactive, so they don't clutter up searches.
""",
    'category': 'Sales',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'depends' : ['base_setup', 'sale', 'sales_team','sale_management'],
    'data': ['views/sale_order_views.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
