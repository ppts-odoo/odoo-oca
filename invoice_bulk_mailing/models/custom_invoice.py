# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models,api,_

# Class to inherit the sale.order    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Account Invoice"

# function to view wizard    
    @api.multi     
    def view_inv_wizard(self):
        invoice_ids = []
        active_ids = self.env.context.get('active_ids',[])
        inv_id = self.env['account.invoice'].search([('id','in',active_ids)])
        for rec in inv_id:
            if rec.state == 'open':
                invoice_ids.append(rec.id)   
        vals = ({'default_inv_ids':invoice_ids})
        return {
            'name':"Send Invoice by Mail",
            'type': 'ir.actions.act_window', 
            'view_type': 'form', 
            'view_mode': 'form',
            'res_model': 'invoice.quote.mail', 
            'target': 'new', 
            'context': vals,
            }
               


        