# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime,timedelta
from odoo import api, fields, models



class res_partner(models.Model):
	_inherit = 'hr.holidays'
	
	@api.one
	@api.depends('date_to')       
	def compute_return_date(self):
		for order in self:
			if order.date_to:
				date_to = datetime.strptime(order.date_to, "%Y-%m-%d %H:%M:%S")
				print"date_todate_todate_to",date_to
				return_date = date_to + timedelta(days=1)
				print"return_datereturn_date",return_date
				order.return_date = return_date.date()
				print"order.return_date",order.return_date

	state = fields.Selection([
		('draft', 'To Submit'),
		('cancel', 'Cancelled'),
		('confirm', 'To Approve'),
		('refuse', 'Refused'),
		('validate1', 'Second Approval'),
		('validate', 'Approved')
		], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
			help="The status is set to 'To Submit', when a holiday request is created." +
			"\nThe status is 'To Approve', when holiday request is confirmed by user." +
			"\nThe status is 'Refused', when holiday request is refused by manager." +
			"\nThe status is 'Approved', when holiday request is approved by manager.")
	
	return_date = fields.Date("Return Date", compute="compute_return_date", store=True)
	
	@api.multi  
	def action_confirm(self):
		if self.filtered(lambda holiday: holiday.state != 'draft'):
			raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
		template_id = self.env.ref('leave_approval.leave_request_mail')
		template_id.send_mail(self.id,force_send=True)
		self.write({'state': 'confirm'})
		return True

	
	
	