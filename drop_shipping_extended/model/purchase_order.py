from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    so_id=fields.Many2one('sale.order')
    do_id=fields.Many2one('stock.picking')
    pro_id=fields.Integer()
    
    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for po in self:
            if po.requisition_id.type_id.exclusive == 'exclusive':
                others_po = po.requisition_id.mapped('purchase_ids').filtered(lambda r: r.id != po.id)
                others_po.button_cancel()
                po.requisition_id.action_done()
            
            
            if not self.so_id:
                for element in po.order_line:
                    if element.product_id == po.requisition_id.procurement_id.product_id:
                        element.move_ids.write({
                            'procurement_id': po.requisition_id.procurement_id.id,
                            'move_dest_id': po.requisition_id.procurement_id.move_dest_id.id,
                        })
                        
            else:
                for element in po.order_line:
                    element.move_ids.write({
                            'reff_line_id': element.pro_id
                        })
            
        return res
    
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    pro_id=fields.Integer()