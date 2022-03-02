# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    minimum_amount = fields.Float('Minimum Amount', implied_group='sale.minimum_amount')
    maximum_amount = fields.Float('Maximum Amount', implied_group='sale.maximum_amount')

    @api.multi
    def set_auto_maximum(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'maximum_amount', self.maximum_amount)

    @api.multi
    def set_auto_minimum(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'minimum_amount', self.minimum_amount)

class SaleOrder(models.Model):
    _inherit = "sale.order"
     
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    approver_id = fields.Many2one('res.users', 'Sale Order Approver', readonly=True, copy=False, track_visibility='onchange', default=lambda self: self.env.user)
    discount_notes = fields.Float('Discount Note')
    next_discount_amount = fields.Float('Next Discount Amount')
    
    @api.multi
    def action_confirm(self):
        for sale_order in self:
            maximum_amount=0.00; minimum_amount =0.00
            if self.env['ir.values'].get_default('sale.config.settings', 'minimum_amount'):
                minimum_amount = float(self.env['ir.values'].get_default('sale.config.settings', 'minimum_amount'))
            if self.env['ir.values'].get_default('sale.config.settings', 'maximum_amount'):
                maximum_amount = float(self.env['ir.values'].get_default('sale.config.settings', 'maximum_amount'))
            if sale_order.amount_total >= minimum_amount and sale_order.amount_total <= maximum_amount:
                if not sale_order.amount_total <= sale_order.approver_id.sale_order_amount_limit:
                    raise UserError(_('Your approval limit is lesser then sale order total amount.Click on "Ask for Approval" for Higher value.'))
                if not sale_order.approver_id == self.env.user:
                    raise UserError(_('You can not confirm this sale order. You have asked for Higher value.'))
        return super(SaleOrder, self).action_confirm()
    
    @api.multi
    def get_discount(self):
        return self.env.context.get('discount_percentage', 0)
    
    @api.multi
    def get_reason_notes(self):
        return self.env.context.get('discount_notes', '')

    @api.multi
    def get_reason_note(self):
        return self.env.context.get('discount_notes', '')
    
    @api.multi
    def escalate_order(self):
        self.ensure_one()
        template = self.env['ir.model.data'].get_object('sale_approval', 'email_template_sale_approval_mail')
        self.env['mail.template'].browse(template.id).send_mail(self.id,force_send=True)
        return True
  
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
     
    @api.onchange('discount')
    def onchang_discount_validate(self):
        if self.discount:
            approver_id = self.order_id.approver_id
            if not self.discount <= approver_id.sale_order_discount_limit:
                value = {
                    'discount': 00.0
                }
                warning = {
                    'title': _('Warning!'),
                    'message' : (_('Your discount limit is lesser than given discount.!'))
                }
                return {'warning': warning, 'value': value}


 

