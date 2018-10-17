# -*- coding: utf-8 -*-

from odoo import models, api, fields
from datetime import datetime, date


class SaleMailSchedule(models.Model):
    _name = 'sale.mail.schedule'
    _description = "Sale mail schedule"
    _rec_name = 'sale_order_id'
    
    schedule_date = fields.Date('Scheduled Date', track_visibility='always')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order', track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('send', 'Send')], default='draft', track_visibility='always')
    send_date = fields.Datetime('Sent Date', track_visibility='always')
    sale_order_state = fields.Char('Sale Order State', compute='_sale_order_state', track_visibility='always')
    order_state = fields.Char('Sale Order State')
    
    @api.depends('sale_order_id')
    def _sale_order_state(self):
        for sale in self:
            if sale.sale_order_id:
                sale.sale_order_state = sale.sale_order_id.state
        
    @api.multi
    def send_now(self):
        for schedule in self:
            template_id = self.env.ref('sale.email_template_edi_sale')
            if template_id:
                template_id.send_mail(schedule.sale_order_id.id, force_send=True)
                schedule.write({'send_date': datetime.now(), 'state':'send'})
                if schedule.sale_order_id.state == 'draft':
                    schedule.sale_order_id.write({'state':'sent'})
        
    @api.multi
    def cron_send_mail(self):
        sale_mail_schedule_id = self.env['sale.mail.schedule'].search([('state', '=', 'draft')])
        for schedule in sale_mail_schedule_id:
            if str(date.today()) == schedule.schedule_date:
                template_id = self.env.ref('sale.email_template_edi_sale')
                if template_id:
                    template_id.send_mail(schedule.sale_order_id.id, force_send=True)
                    schedule.write({'send_date': datetime.now(), 'state':'send'})
                    if schedule.sale_order_id.state == 'draft':
                        schedule.sale_order_id.write({'state':'sent'})

