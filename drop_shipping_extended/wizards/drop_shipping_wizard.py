from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class DropShippingWizard(models.TransientModel):
    _name = "drop.ship.wizard"
    
    line_ids=fields.One2many('drop.ship.wizard.line','order_id',string='Order Lines')
    
    @api.model
    def default_get(self,vals):
        terms=[]
        ds_obj=self.env['drop.ship.wizard.line']
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        
        if stock_obj.picking_type_id.name == 'Dropship':
            raise UserError(_('This process cannot be done'))
        if stock_obj.state!='done' and stock_obj.state !='cancel':
            so=self.env['sale.order'].search([('name','=',stock_obj.origin)])
            for obj in stock_obj.move_lines:
                if obj.state != 'cancel' and obj.state != 'done':
                    vendor_id=0
                    temp=0
                    for sell in obj.product_id.seller_ids:
                            if temp==0:
                                vendor_id=sell.name.id
                                temp+=1
                                
                    terms.append((0, 0, {'product_id':obj.product_id.id,'ref_id':obj.id,'product_qty':obj.product_qty,'product_uom':obj.product_uom.id,'unit_price':obj.product_id.standard_price,'vendor_id':vendor_id,'drop_boolean' : False,'procurement_id':obj.procurement_id.sale_line_id.id}))
            res = super(DropShippingWizard, self).default_get(vals)      
            res.update({'line_ids': terms})
        else:
             raise UserError(_('Cannot create Drop shippig for Done orders'))
            
        return res
        
    
    def action_create_drop_ship(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        so=self.env['sale.order'].search([('name','=',stock_obj.origin)])
        sale_origin=stock_obj.origin
        del_origin=stock_obj.name
        vendor_id=0
        po_id=0
        poc=0
        po=self.env['purchase.order']
        for obj in self.line_ids:
            if obj.vendor_id:
                if obj.drop_boolean and obj.record_id:
                    vals={
                        'partner_id':obj.vendor_id.id,
                        'origin': sale_origin + del_origin,
                        'picking_type_id':25,
                        'dest_address_id':so.partner_id.id,
                        'so_id':so.id,
                        'do_id':stock_obj.id,
                        'group_id':stock_obj.group_id.id
                        }
                    vendor_id=obj.vendor_id.id
                    date=datetime.now()
                    po_id=po.create(vals)
                    line_vals={
                        'product_id':obj.product_id.id,
                        'order_id':po_id.id,
                        'product_uom':obj.product_uom.id,
                        'product_qty':obj.product_qty,
                        'price_unit':obj.unit_price,
                        'name':obj.product_id.name,
                        'date_planned':date,
                        'pro_id':obj.procurement_id
                     }
                    obj.record_id=False
                    pol_id=self.env['purchase.order.line'].create(line_vals)
                    sop=self.env['stock.move'].search([('picking_id','=',stock_obj.id),('product_id','=',obj.product_id.id),('id','=',obj.ref_id)])
                    if sop.product_uom_qty==obj.product_qty:
                        sop.state='cancel'
                    elif obj.product_qty < sop.product_uom_qty:
                        sop.product_uom_qty-=obj.product_qty
                    else:
                        raise UserError(_('Product Quantity exceeds the original quantity for %s') %(obj.product_id.name))
                    for ob in self.line_ids:
                        if ob.drop_boolean and ob.vendor_id:
                            if vendor_id==ob.vendor_id.id and ob.record_id:
                                line_vals={
                                    'product_id':ob.product_id.id,
                                    'order_id':po_id.id,
                                    'product_uom':ob.product_uom.id,
                                    'product_qty':ob.product_qty,
                                    'price_unit':ob.unit_price,
                                    'name':ob.product_id.name,
                                    'date_planned':date,
                                    'pro_id':ob.procurement_id
                                }
                                ob.record_id=False
                                pol_id=self.env['purchase.order.line'].create(line_vals)
                                sop=self.env['stock.move'].search([('picking_id','=',stock_obj.id),('product_id','=',ob.product_id.id),('id','=',ob.ref_id)])
                                if sop.product_uom_qty==ob.product_qty:
                                    sop.state='cancel'
                                elif ob.product_qty < sop.product_uom_qty:
                                    sop.state='draft'
                                    sop.product_uom_qty-=ob.product_qty
                                else:
                                    raise UserError(_('Product Quantity exceeds the original quantity for %s') %(ob.product_id.name))
                                
            else:
                raise UserError(_('No Vendpr Configured For Product  %s') %(obj.product_id.name))
        stock_obj=self.env['stock.picking'].search([('id','=',active_ids)])
        if(len(stock_obj.move_lines))==0:
            stock_obj.state='cancel'
            stock_obj.message_post(body=_("Purchase Order Created For this Sale order"))
        else:
            stock_obj.message_post(body=_("Purchase Order Created For this Sale order."))  
class DropShippingWizardLine(models.TransientModel):
    _name = 'drop.ship.wizard.line'
    
    drop_boolean=fields.Boolean(string='Drop Ship')
    order_id=fields.Many2one('drop.ship.wizard')
    product_id = fields.Many2one('product.product',string="Product")
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    unit_price=fields.Float()
    vendor_id=fields.Many2one('res.partner')
    record_id=fields.Boolean(default=True)
    ref_id=fields.Integer()
    procurement_id=fields.Integer(string='Procurement_id')
