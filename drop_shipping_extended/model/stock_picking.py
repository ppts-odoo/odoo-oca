from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        po=self.env['purchase.order'].search([('name','=',self.origin)])
        if po:
            for  obj in self.move_lines:
               
                if obj.reff_line_id:
                    so=self.env['sale.order.line'].search([('order_id','=',po.so_id.id),('product_id','=',obj.product_id.id),('id','=',obj.reff_line_id)])
                else:
                    so=obj.sale_line_id
                
                if so:
                    so.qty_delivered+=obj.product_qty
                else:
                    so=self.env['sale.order.line'].search([('order_id','=',po.so_id.id),('product_id','=',obj.product_id.id),('id','=',obj.reff_line_id)])
                    if so:
                        so.qty_delivered+=obj.product_qty
                    
        return res
    
    
    
    @api.model
    def action_create_drop_shipping(self):
        self.ensure_one()
        return {
            'name': 'Create Drop Shipping',
            'type': 'ir.actions.act_window',
            'res_model': 'drop.ship.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': self.env.context,
            'target': 'new',
        }
        
    @api.model
    def action_create_delivery_order(self):
        self.ensure_one()
        return {
            'name': 'Create Delivery Order',
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.order.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': self.env.context,
            'target': 'new',
        }
    

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    reff_line_id=fields.Integer()