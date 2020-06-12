# -*- coding: utf-8 -*-

from odoo import models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_schedule_wizard(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        act_id = context.get('active_ids', False)
        order_list = []
        schedule_ids = self.env['sale.mail.schedule'].search([('sale_order_id','in',(act_id))])
        order_ids = self.env['sale.order'].browse(act_id)
        for schedule in schedule_ids:
            for order in order_ids:
                if order.id == schedule.sale_order_id.id:
                    if order.state == schedule.order_state:
                        order_list.append(schedule.sale_order_id.name)
        if order_list:
            l = ''
            for x in order_list:
                if l == '':
                    l += x
                else:
                    l += ',' + x
            raise Warning(_('%s already exits.') % (l))   
        else:
            return {
                'name': _('Mail Scheduler Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.mail.schedule.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'context': context,
                'target': 'new'
            }
