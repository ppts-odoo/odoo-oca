from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    
    def do_new_transfer(self):
        res = super(StockPicking, self).do_new_transfer()
        po=self.env['purchase.order'].search([('name','=',self.origin)])
        if po:
            for  obj in self.move_lines:
                so=self.env['sale.order.line'].search([('order_id','=',po.so_id.id),('product_id','=',obj.product_id.id),('id','=',obj.reff_line_id)])
                if so:
                    so.qty_delivered+=obj.product_qty
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    reff_line_id=fields.Integer()