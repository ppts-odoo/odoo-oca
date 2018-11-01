# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.http import request

from datetime import datetime,timedelta

_logger = logging.getLogger(__name__)
 
class Example(http.Controller):

	@http.route('/leaveapproval/<employee_id>/<id>', type='http', auth='public', website=True)
	def example_page(self,*args, **kw):
		employee_id = int(kw['employee_id'])
		id = int(kw['id'])
		values = http.request.env['hr.holidays'].sudo().search([('employee_id', '=', employee_id),('id', '=', id)])
		value = {
				'values':values,
			  }
		return http.request.render('leave_approval.example_page', value)


	@http.route('/approvalmail', type='http', auth='public', website=True,  csrf=False)
	def action_approve(self, *args, **post):
		print post,'posttttttttttt'
		holiday_id = int(post.get('hr_holidays'))
		
		holiday_obj= http.request.env['hr.holidays'].sudo().search([('id', '=', holiday_id)])

		
		if holiday_obj:
			print '=======',
			if holiday_obj.holiday_status_id.double_validation == True:
				
				if holiday_obj.state == 'confirm':
					value = {
						'values':holiday_obj,
					  }
					holiday_obj.action_approve()
					template_id = request.env.ref('leave_approval.leave_validation_mail')
					print '=====',template_id,holiday_id
					template_id.send_mail(holiday_id, force_send=True)
					return http.request.render('leave_approval.submit')
				
				
				if holiday_obj.state =='validate1':
					value = {
						'values':values,
					  }
					holiday_obj.action_validate()
					template_id = request.env.ref('leave_approval.leave_validation_mail')
					template_id.send_mail(holiday_id, force_send=True)
					return http.request.render('leave_approval.validation_page',value)
				
			else:
				if holiday_obj.state == 'confirm':
					value = {
						'values':holiday_obj,
					  }
					holiday_obj.action_approve()
					template_id = request.env.ref('leave_approval.leave_approval_mail')
					print '=====',template_id,holiday_id
					template_id.send_mail(holiday_id, force_send=True)
					return http.request.render('leave_approval.submit')


	@http.route('/approvalvalidationmail/<employee_id>/<id>', type='http', auth='public', website=True)
	def action_approve_validate(self,*args, **kw):
		employee_id = int(kw['employee_id'])
		id = int(kw['id'])
		values = http.request.env['hr.holidays'].sudo().search([('employee_id', '=', employee_id),('id', '=', id)])
		value = {
				'values':values,
			  }

		return http.request.render('leave_approval.validation_page', value)

	@http.route('/approvalvalidationmail', type='http', auth='public', website=True,  csrf=False)
	def action_validate(self, *args, **post):
		print post,'posttttttttttt'
		holiday_id = int(post.get('hr_holidays'))
		holiday_obj= http.request.env['hr.holidays'].sudo().search([('id', '=', holiday_id)])

		if holiday_obj:
			print '23333333333',
			if holiday_obj.holiday_status_id.double_validation == True:
				print '******',holiday_obj.state
				if holiday_obj.state =='validate1':
					
					holiday_obj.action_validate()
					template_id = request.env.ref('leave_approval.leave_approval_mail')
					template_id.send_mail(holiday_id, force_send=True)
					return http.request.render('leave_approval.submit')

			else:
				holiday_obj.action_validate()
				return http.request.render('leave_approval.submit')

	
		


	@http.route('/refusemail', type='http', auth='public', website=True,  csrf=False)
	def action_refuse(self, *args, **post):
		print 'oooooooooooooooooo',post
		holiday_id = int(post['hr_holiday'])
		print '&&&&&&&&&&',holiday_id
		holiday_obj= http.request.env['hr.holidays'].sudo().search([('id', '=', holiday_id)])
		print('dddddddddddddd',holiday_obj)
		if holiday_obj:
			if holiday_obj.holiday_status_id.double_validation == True:
				print '******',holiday_obj.state
				if holiday_obj.state in ('confirm','validate1'):
					
					holiday_obj.action_refuse()
					template_id = request.env.ref('leave_approval.leave_rejection_mail')
					template_id.send_mail(holiday_id, force_send=True)
					return http.request.render('leave_approval.submit')

			if holiday_obj.state in ('confirm'):
					
				holiday_obj.action_refuse()
				template_id = request.env.ref('leave_approval.leave_rejection_mail')
				template_id.send_mail(holiday_id, force_send=True)
				return http.request.render('leave_approval.submit')
		
