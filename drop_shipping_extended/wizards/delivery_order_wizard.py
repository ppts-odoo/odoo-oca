from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class DeliveryOrderWizard(models.TransientModel):
    _name = "delivery.order.wizard"
    
    line_ids=fields.One2many('delivery.order.wizard.line','order_id',string='Order Lines')
    
    
    @api.model
    def default_get(self,vals):
        terms=[]
        ds_obj=self.env['delivery.order.wizard.line']
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        if stock_obj.picking_type_id.name == 'Delivery Orders':
            raise UserError(_('This process cannot be done'))
        if stock_obj.state!='done' and stock_obj.state!='cancel':
            so=self.env['sale.order'].search([('name','=',stock_obj.origin)])
            for obj in stock_obj.move_lines:
                if obj.state != 'cancel'  and obj.state !='done':
                    vendor_id=0
                    temp=0
                    sol=self.env['sale.order.line'].search([('order_id','=',so.id),('product_id','=',obj.product_id.id)])
                    for sell in obj.product_id.seller_ids:
                            if temp==0:
                                vendor_id=sell.name.id
                                temp+=1
                                
                    terms.append((0, 0, {'product_id':obj.product_id.id,'ref_id':obj.id,'product_qty':obj.product_qty,'product_uom':obj.product_uom.id,'drop_boolean' : False,'procurement_id':obj.sale_line_id.id,'reff_line_id':obj.reff_line_id}))
        res = super(DeliveryOrderWizard, self).default_get(vals)      
        res.update({'line_ids': terms})
        return res
    
    
    
    def action_create_delivery_order(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        po_obj=self.env['purchase.order'].search([('name','=',stock_obj.origin)])
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        stock_obj1=self.env['stock.picking']
        sm=self.env['stock.move']
        
        so=self.env['sale.order'].search([('name','=',stock_obj.group_id.name)])
        if not so.warehouse_id.out_type_id.default_location_dest_id.id:
            raise UserError(_('Configure Warehouse Destination Location'))
            
        if so:
            so.warehouse_id.out_type_id.default_location_src_id
        
            vals={
                'partner_id':stock_obj.partner_id.id,
                'location_id':so.warehouse_id.out_type_id.default_location_src_id.id,
                'location_dest_id':so.warehouse_id.out_type_id.default_location_dest_id.id,
                'origin':stock_obj.origin,
                'priority':stock_obj.priority,
                'picking_type_id':so.warehouse_id.out_type_id.id,
                }
            grop_id={
                'group_id':stock_obj.group_id.id
                }
            date=datetime.now()
            sp_id=stock_obj1.create(vals)
        for obj in self.line_ids:
            if obj.drop_boolean:
                line_vals={
                'product_id':obj.product_id.id,
                'product_uom_qty':obj.product_qty,
                'product_uom':obj.product_uom.id,
                'picking_id':sp_id.id,
                'state':'draft',
                'name':obj.product_id.name,
                'location_id':so.warehouse_id.out_type_id.default_location_src_id.id,
                'location_dest_id':so.warehouse_id.out_type_id.default_location_dest_id.id,
                'procure_method':'make_to_stock',
                'date_expected':date,
                'weight':0,
                'reff_line_id':obj.reff_line_id,
                'sale_line_id':obj.procurement_id
                }
                sm_id=sm.create(line_vals)
                l_grop_id={
                    'group_id':stock_obj.group_id.id,
#                     'sale_line_id':obj.procurement_id
                    }
                sm_id.update(l_grop_id)
                sop=self.env['stock.move'].search([('picking_id','=',stock_obj.id),('product_id','=',obj.product_id.id),('id','=',obj.ref_id)])
                if sop.product_uom_qty==obj.product_qty:
                    sop.state='cancel'
                elif obj.product_qty < sop.product_uom_qty:
                    sop.product_uom_qty-=obj.product_qty
                else:
                    raise UserError(_('Product Quantity exceeds the original quantity for %s') %(obj.product_id.name))
        
        sp_id.update(grop_id)
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        if((stock_obj.state))=='cancel':          
                po_obj.button_cancel()
        po_obj.message_post(body=_("Delivery Order Created For this Purchase Order"))
        
        stock_obj.message_post(body=_("Delivery Order Created For this Purchase Order"))
class DeliveryOrderWizardLine(models.TransientModel):
    _name = 'delivery.order.wizard.line'
    
    drop_boolean=fields.Boolean(string='Delivery Order')
    order_id=fields.Many2one('delivery.order.wizard')
    product_id = fields.Many2one('product.product',string="Product")
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    ref_id=fields.Integer()
    procurement_id=fields.Integer()
    reff_line_id=fields.Integer()
    
    
    