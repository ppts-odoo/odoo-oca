# -*- encoding: utf-8 -*-
{
	"name": "Leave Mail Approval",
	"version": "10.0",
	"author": "PPTS [India] Pvt.Ltd.",
	"website": "http://www.pptssolutions.com",
	"sequence": 0,
	"depends": [
		"base", "mail", "contacts", "hr_holidays", "website"],
	"category": "Settings",
	"complexity": "easy",
	
	"data": [
		
		'views/leave_approval_view.xml',
		'views/controller_view.xml',
		'data/leave_request_view.xml'
	],
	"demo": [
	],
	"test": [
	],
	"auto_install": False,
	"installable": True,
	"application": False,
    'images': ['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
