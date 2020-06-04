# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api,fields, models

# class to create wizard
class PurchaseOrderMassMail(models.TransientModel):
    _name="purchase.quote.mail"
    
    po_ids = fields.Many2many('purchase.order',string="Purchase Orders",required=True, domain=[('state', 'in', ['draft', 'sent', 'purchase'])])
   
# function to send po/quote bulk mail   
    def send_mail(self):
        vals = self.po_ids
        for order in vals:
            email_act = order.action_rfq_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True
