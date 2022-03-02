# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleApprovalReason(models.TransientModel):
    _name = 'sale.approval.reason'
    
    approval_for = fields.Selection([
    ('for_amount', 'Request For Amount'),
    ('for_discount', 'Request For Discount'),
    ], 'Approve Type', copy=False, required=True, select=True)
    requested_discount = fields.Float('Requested Discount')
    notes = fields.Text('Notes')
     
    def approve(self):
        sale_br_obj = self.env['sale.order'].browse(self._context.get('active_ids'))[0]
        user_obj = self.env['res.users']
        if self.approval_for == 'for_amount':
            user_search = user_obj.search([('sale_order_amount_limit', '>=', sale_br_obj.amount_total), ('sale_order_can_approve', '=', 'yes')], order='sale_order_amount_limit')
            if user_search:
                next_larg_amount_user_id = user_search[0]
            else:
                raise UserError('Approver is not set for this Amount Limit. Please allocate approver')
            sale_br_obj.write({'approver_id': next_larg_amount_user_id.id, 'state': 'waiting_for_approval'})
        if self.approval_for == 'for_discount':
            if self.requested_discount:
                user_search_discount = user_obj.search([('sale_order_discount_limit', '>=', self.requested_discount)], order='sale_order_discount_limit')
                if user_search_discount:
                    discount_approver_user_id = user_search_discount[0]
                else:
                    raise UserError('Approver is not set for this Amount Limit. Please allocate approver')
                sale_br_obj.write({'approver_id': discount_approver_user_id.id, 'next_discount_amount': self.requested_discount, 'state': 'waiting_for_approval'})
        ctx = self.env.context.copy()
        ctx.update({'discount_percentage': float(self.requested_discount), 'discount_notes': str(self.notes)})
        sale_br_obj.with_context(ctx).escalate_order()
        return True