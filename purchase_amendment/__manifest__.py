# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Amendment',
    'version' : '1.1',
    'summary': 'Purchase Amendment',
    'sequence': 30,
    'description': """ Purchase Order Amendment
When user need to modify/amend a product/quantity/price in a confirmed purchase order, user should not modify it in the purchase order directly. The purchase order represents what the supplier really supplied. The changes would not be repercuted on the incoming shipments and invoices neither.
But this module allows the user can do modify / amend on confirmed  orders. Once user click on the "Amendment" button, then this will create the same order in editable mode, with the same base number and a '-XXX' suffix appended. A message is added in the chatter saying that a new revision was created.
In the form view, a new tab is added that lists the previous revisions, with the date they were made obsolete and the user who performed the action.
The old revisions/amendments of a purchase order are flagged as inactive, so they don't clutter up searches.""",
    'category': 'Purchase',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'images' : [],
    'depends' : ['base_setup', 'purchase'],
    'data': ['views/purchase_views.xml',
             'views/purchase_amendment_view.xml',
             'security/ir.model.access.csv',
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
