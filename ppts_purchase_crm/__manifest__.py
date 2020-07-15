# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{   
	"name": "Purchase CRM",
	"version": "13.0",
	'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
	"sequence": 0,
	"depends": ["base",'sale_crm','purchase'],
	"category": "CRM",
	"description": """
		This module allows to add purchase quotation from lead. 
	""",
	"data": [
		'views/crm_view.xml',
		'security/ir.model.access.csv',
	],
	"auto_install": False,
	"installable": True,
	"application": True,
    'images': ['static/description/banner.png'],
}
