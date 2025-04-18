# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def bulk_products(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].check_object_reference('sale_bulk_products', 'order_bulk_products_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.bulk',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }  
               
      
class OrderBulkProducts(models.TransientModel):
    _name = 'sale.order.bulk'    
    
    bulk_id = fields.Many2many('product.product', 'bulk_product_rel')   
        
    def confirm_products(self):
        val = {}
        context = dict(self._context or {})
        active_id = context.get('active_id')
        sale_obj = self.env['sale.order'].search([('id','=',active_id)])
        line_ids = []
        for loop in self.bulk_id:
            val = ({
                    'product_id': loop.id,})
            line_ids.append((0, 0, val))
        sale_obj.update({'order_line': line_ids })                 
                                 