# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    @api.multi
    def bulk_products(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('sale_bulk_products', 'order_bulk_products_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.bulk',
#             'res_id': self.product_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
        }  
        
class OrderBulkProducts(models.TransientModel):
    _name = 'sale.order.bulk'    
    
    bulk_id = fields.Many2many('product.product', 'bulk_product_rel')   
    
    
    @api.multi
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
                                 
      
class ProductProduct(models.Model):
    _inherit = 'product.product'    
    
    bulk_product_id = fields.Many2many('sale.order.bulk', 'bulk_product_rel')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
