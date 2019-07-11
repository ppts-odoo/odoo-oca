# -*- encoding: utf-8 -*-
{
	"name": "Assign and Unassign Followers",
	"version": "12.0",
	"author": "PPTS [India] Pvt.Ltd.",
	"website": "http://www.pptssolutions.com",
	"sequence": 0,
	"depends": [
		"base","mail"
	],
	"category": "Settings",
	"complexity": "easy",
	'license': 'LGPL-3',
    'support': 'business@pptservices.com',
	"description": """
	Assign Followers to a Record of any Model
	""",
	"data": [
		
		'security/base_groups.xml',
		'security/ir.model.access.csv',
		'views/assign_followers_view.xml',
	
		
	],
	"demo": [
	],
	"test": [
	],
    'images': ['static/description/banner.png'],
	"auto_install": False,
	"installable": True,
	"application": False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
