# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models,api,_

# Class to inherit the sale.order    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sales Order"

# function to view wizard    
    @api.multi     
    def view_wizard(self):
        sale_ids = []
        active_ids = self.env.context.get('active_ids',[])
        sale_id = self.env['sale.order'].search([('id','in',active_ids)])
        for rec in sale_id:
            if rec.state == 'sale' or rec.state == 'draft' or rec.state == 'sent'  :
                sale_ids.append(rec.id)    
        vals = ({'default_sale_order_ids':sale_ids})
        return {
            'name':"Send SO/Quotation by Mail",
            'type': 'ir.actions.act_window', 
            'view_type': 'form', 
            'view_mode': 'form',
            'res_model': 'so.quote.mail', 
            'target': 'new', 
            'context': vals
            }
               
               


        