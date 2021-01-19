from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    so_id=fields.Many2one('sale.order')
    do_id=fields.Many2one('stock.picking')
    pro_id=fields.Integer()
    
   
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for element in self.order_line:
            element.move_ids.write({
                    'reff_line_id': element.pro_id
                })
               
        return res
   
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    pro_id=fields.Integer()