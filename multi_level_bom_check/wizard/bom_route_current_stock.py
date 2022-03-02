# Copyright 2018 Camptocamp SA
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class BomRouteCurrentStock(models.TransientModel):
    _name = "mrp.bom.current.stock"
    _description = 'MRP Bom Route Current Stock'

    bom_id = fields.Many2many(
        comodel_name="mrp.bom",
        string="Starting Bill of Materials",
        required=True,
    )
    product_id = fields.Many2many(
        comodel_name='product.product',
        string='Product Variant',
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
    )
    product_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
    )
    location_id = fields.Many2many(
        comodel_name="stock.location",
        string="Starting location",
    )
    line_ids = fields.One2many(
        comodel_name='mrp.bom.current.stock.line',
        inverse_name='explosion_id',
    )
   
    qty_produce = fields.Integer(
        string='Quantity to produce',
    )
    company_id = fields.Many2one(comodel_name='res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one(comodel_name='res.users', string='User', readonly=True,
                                 default=lambda self: self.env.user)
    
    allow_multi_level = fields.Boolean("Allow Multilevel")
    report_type = fields.Char("Type",compute="_compute_report_type",)
    
#     @api.multi
    def _compute_report_type(self):
        for recs in self:
            if recs.allow_multi_level == True:
                recs.report_type = 'Multi Level'
            else:
                recs.report_type = 'Top Level'  
            
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         for product_ids in self.product_id:
#             self.bom_id = self.env['mrp.bom']._bom_find(
#                 product_tmpl=product_ids,
#             )

#     @api.onchange('bom_id')
#     def _onchange_bom_id(self):
#         if self.bom_id.location_id:
#             self.location_id = self.bom_id.location_id


    @api.model
    def _prepare_qty_available_tot(self, product_id, location):
        tot_qty_lis = 0
        qty_ids_loc = self.env['stock.quant'].search([('product_id','=',product_id),('location_id','in',self.location_id.ids)])
        for locs_id in qty_ids_loc:
            tot_qty_lis += locs_id.quantity
        return tot_qty_lis 

    @api.model
    def _prepare_qty_available(self, product_id, location):
        tot_qty_lis = 0
        qty_ids_loc = self.env['stock.quant'].search([('product_id','=',product_id),('location_id','=',location)])
        if qty_ids_loc:
            tot_qty_lis = qty_ids_loc.quantity
        return tot_qty_lis   

    @api.model
    def _prepare_res_qty(self, product_id, location):
        
        total_qty = 0
        qty_ids = self.env['stock.move'].search([('product_id','=',product_id),('state','in',('partially_available','assigned')),('location_id','=',location)])
        
        for qty_id in qty_ids:
            total_qty += qty_id.reserved_availability
        return  total_qty   

    @api.model
    def _prepare_line(self, bom_line, level, factor , qty_produce_multi , bom_ids):
        
        list_lines = []
        for loc in self.location_id:
            stock_qt_ids = self.env['stock.quant'].search([('product_id','=',bom_line.product_id.id),('location_id','in',self.location_id.ids)])
            test_loc=''
            for list_lines_loc in stock_qt_ids:
                test_loc = test_loc + list_lines_loc.location_id.name +': '+ str(list_lines_loc.quantity) +','
            
            vals_line = {
                'product_id': bom_line.product_id.id,
                'product_name':bom_line.product_id.name,
                'bom_line': bom_line.id,
                'bom_level': level,
                'product_qty': bom_line.product_qty * factor * qty_produce_multi,
                'reserved_qty': self._prepare_res_qty(bom_line.product_id.id, loc.id),
                'product_uom_id': bom_line.product_uom_id.id,
                'location_id': (bom_line.location_id.id
                                if bom_line.location_id else loc.id),
                'explosion_id': self.id,
                'parent_id': bom_ids.id,
                'loc_list':test_loc,
                'qty_available_in_source_loc':self._prepare_qty_available(bom_line.product_id.id, loc.id),
                'tot_qty_avail':self._prepare_qty_available_tot(bom_line.product_id.id, loc.id),
            }
            list_lines.append(vals_line)
            
        return list_lines
    
    def do_explode(self):
#         if self.allow_multi_level == False:
         
        self.ensure_one()
        line_obj = self.env['mrp.bom.current.stock.line']

        def _create_lines(bom, level=0, factor=1):
            qty_produce_multi = 0
            if self.qty_produce > 0:
                qty_produce_multi = self.qty_produce
            else:
                qty_produce_multi = 1   
            
            level += 1
            for line in bom.bom_line_ids:
#                 print(line,"line")
#                 print(line.product_id.name,"line")
                vals = self._prepare_line(line, level, factor , qty_produce_multi, bom_ids)
                line_obj.create(vals)
                location = line.location_id
                line_boms = line.product_id.bom_ids
                boms = line_boms.filtered(
                    lambda bom: bom.location_id == location
                ) or line_boms.filtered(lambda b: not b.location_id)
                print(boms,"bomd")
                if self.allow_multi_level == True:
                    if boms:
                        line_qty = line.product_uom_id._compute_quantity(
                            line.product_qty,
                            boms[0].product_uom_id,
                        )
                        new_factor = factor * line_qty / boms[0].product_qty
                        _create_lines(boms[0], level, new_factor)

        for bom_ids in self.bom_id:
            _create_lines(bom_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open lines',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'mrp.bom.current.stock',
            'view_id': self.env.ref(
                'multi_level_bom_check.mrp_bom_current_stock_view_form2'
            ).id,
            'target': 'new',
            'res_id': self.id,
                }


class BomRouteCurrentStockLine(models.TransientModel):
    _name = "mrp.bom.current.stock.line"
    _description = 'MRP Bom Route Current Stock Line'

    explosion_id = fields.Many2one(
        comodel_name='mrp.bom.current.stock',
        readonly=True
    )
    product_name = fields.Char(
        readonly=True,string="Product"
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Ref No.',
        readonly=True,
    )
    bom_level = fields.Integer(
        string='BoM Level',
        readonly=True
    )
    product_qty = fields.Float(
        string='Product Quantity',
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
    )
    reserved_qty = fields.Float(
        string='Reserved Quantity',
        readonly=True,
    )
    shortage_qty = fields.Float(
        string='Quantity Shortage',
        compute="_compute_shortage_qty",
        readonly=True,
    )
    
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product Unit of Measure',
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source location",
    )
    bom_line = fields.Many2one(
        comodel_name="mrp.bom.line",
        string="BoM line",
        redonly=True
    )
    qty_available_in_source_loc = fields.Float(
        string="Qty Available in Source",
        redonly=True
    )
    bom_id = fields.Many2one(comodel_name="mrp.bom", string="Parent BoM",
                             related='bom_line.bom_id', redonly=True)
    
    parent_id = fields.Many2one(comodel_name="mrp.bom",
        string="Parent ID",
    )
    loc_list = fields.Text(
        string="list",
    )
    
    tot_qty_avail = fields.Integer(
        string="Tot",
    )
    
    tot_qty_avail_shortage = fields.Integer(
        string="Tot",compute="_compute_shortage_qty_total",
    )
    
    forecasted_qty = fields.Float(
        string="Forecasted Quantity",compute="_compute_forecasted_qty",
    )
    
#     forecasted_qty_total = fields.Float(
#         string="Forecasted Quantity Total",compute="_compute_forecasted_qty_total",
#     )
    
#     @api.multi
#     def _compute_parent_id(self):
#         for line_ids_items in self:
#             for line_ids_parent in line_ids_items.explosion_id.bom_id:
#                 if line_ids_items.bom_id == line_ids_parent:
#                     line_ids_items.parent_id = line_ids_parent
            
#             for line_ids_parent in line_ids_items.explosion_id.bom_id:
#                 if line_ids_parent.product_id.bom_ids == line_ids_parent:
#                     line_ids_items.parent_id = line_ids_parent

#     @api.multi
#     @api.onchange('location_id')
#     def _compute_qty_available_in_source_loc(self):
#         for record in self:
#             product_available = record.product_id.with_context(
#                 location=record.location_id.id
#             )._product_available()[record.product_id.id]['qty_available']
#             res = record.product_id.product_tmpl_id.uom_id._compute_quantity(
#                 product_available,
#                 record.product_uom_id,
#             )
#             record.qty_available_in_source_loc = res
#     @api.model
#     def _prepare_tot_forecasted(self, tot_vals):
#         final_qty = 0
#         for recs in tot_vals:
#             prod_ids = self.env['product.product'].search([('id','=',recs)])
#             final_qty +=prod_ids.virtual_available
#         return final_qty    

#     @api.multi
#     def _compute_forecasted_qty_total(self):
#         tot_vals = []
#         for recs in self:
#             tot_vals.append(recs.product_id.id)    
#         recs.forecasted_qty_total = self._prepare_tot_forecasted(tot_vals)      
                 
    def _compute_forecasted_qty(self):
        for recs in self:
            qty_stock = recs.qty_available_in_source_loc
            print(qty_stock)
            
            so_qty = 0
            qty_so_ids = self.env['stock.move'].search([('product_id','=',recs.product_id.id),('state','=','partially_available'),('location_id','=',recs.location_id.id)])
            for qty_so in qty_so_ids:
                so_qty += qty_so.reserved_availability
            print(so_qty)   
             
            mo_qty = 0
            qty_mo_ids = self.env['stock.move'].search([('product_id','=',recs.product_id.id),('state','=','assigned'),('location_id','=',recs.location_id.id)])
            for qty_mo in qty_mo_ids:
                mo_qty += qty_mo.reserved_availability    
            print(mo_qty)   
             
            po_qty = 0
            qty_po_ids = self.env['stock.move'].search([('product_id','=',recs.product_id.id),('state','=','assigned'),('location_dest_id','=',recs.location_id.id)])
            for qty_po in qty_po_ids:
                po_qty += qty_po.reserved_availability      
             
            print(po_qty)    
            
            recs.forecasted_qty =(qty_stock + po_qty )-(so_qty + mo_qty)
            so_qty = mo_qty = po_qty = 0
            
            
#             if recs.product_id.virtual_available:
#                 recs.forecasted_qty = recs.product_id.virtual_available
  
    
    def _compute_shortage_qty_total(self):
        for rec in self:
            if rec.tot_qty_avail < rec.product_qty:
                rec.tot_qty_avail_shortage = rec.product_qty - rec.tot_qty_avail 
            else:
                rec.tot_qty_avail_shortage = 0  
        
    
    def _compute_shortage_qty(self):
        for rec in self:
            if rec.forecasted_qty < rec.product_qty:
                rec.shortage_qty = rec.product_qty - rec.forecasted_qty 
            else:
                rec.shortage_qty = 0    
                      
            
            
