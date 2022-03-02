# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models,api,_

# Class to inherit the sale.order    
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"

# function to view wizard    
    def view_po_wizard(self):
        purchase_ids = []
        active_ids = self.env.context.get('active_ids',[])
        purchase_id = self.env['purchase.order'].search([('id','in',active_ids)])
        for rec in purchase_id:
            if rec.state in ('purchase','draft','sent'):
                purchase_ids.append(rec.id)    
        vals = ({'default_po_ids':purchase_ids})
        return {
            'name':"Send Purchase/Quotation by Mail",
            'type': 'ir.actions.act_window', 
            'view_type': 'form', 
            'view_mode': 'form',
            'res_model': 'purchase.quote.mail', 
            'target': 'new', 
            'context': vals
            }
               


        