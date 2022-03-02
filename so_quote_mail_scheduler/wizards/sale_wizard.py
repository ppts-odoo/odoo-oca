# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleMailScheduler(models.TransientModel):

    _name = "sale.mail.schedule.wizard"
    _description = "Sale mail schedule wizard"

    schedule_date = fields.Date('Schedule Date', required=True)

    def done(self):
        context = dict(self.env.context or {})
        act_id = context.get('active_ids', False)
        for act in act_id:
            order_id = self.env['sale.order'].browse(act)
            self.env['sale.mail.schedule'].create({
                'schedule_date':self.schedule_date,
                'sale_order_state':order_id.state,
                'sale_order_id':act
            })
        return {'type': 'ir.actions.act_window_close'}