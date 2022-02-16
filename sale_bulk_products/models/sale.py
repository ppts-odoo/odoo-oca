# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

#     @api.multi
    def bulk_products(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].check_object_reference('sale_bulk_products', 'order_bulk_products_form')
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
        
        
         
#     @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        for order in orders_to_plan:
            quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
            boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
            order._generate_workorders(boms)
        return orders_to_plan.write({'state': 'planned'})   
        
        
      
class OrderBulkProducts(models.TransientModel):
    _name = 'sale.order.bulk'    
    
    bulk_id = fields.Many2many('product.product', 'bulk_product_rel')   
    
    
#     @api.multi
    def confirm_products(self):
        val = {}
        context = dict(self._context or {})
        active_id = context.get('active_id')
        print(active_id,'11111111111111111111111111111111111')
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
