# -*- coding: utf-8 -*-
from odoo import api, fields, models,tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
import os

class stock(models.Model):   
    _inherit = "stock.move"
    
    file_import = fields.Binary("Import File", help="*Import a list of lot/serial numbers from a csv file \n *Only csv files is allowed"
                                                              "\n *The csv file must contain a row header namely 'Serial Number'")
    file_name = fields.Char("file name")
    
#     importing "csv" file and appending the datas from file to order lines 
    @api.multi
    def input_file(self):
        if self.file_import:
            file_value = self.file_import.decode("utf-8")
            filename,FileExtension = os.path.splitext(self.file_name)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import the 'csv' file")
            data_list = []
            input_file = base64.b64decode(file_value)
            lst = []
            for loop in input_file.decode("utf-8"):
                lst.append(loop)
            lsts = input_file.decode("utf-8").split("\n")
            
            if 'Serial Number' not in lsts[0]:
                    raise UserError ('Row header name "Serial Number" is not found in CSV file')
            lsts.pop(0)
            for rec in lsts:
                if rec:
                    data = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id),('name','=',str(rec))])
#                     list values for move_line_ids 
                    data_list.append((0,0,{'lot_id':data.id,
                                            'qty_done': 1,
                                            'product_uom_qty' : 1,
                                            'product_uom_id' : self.product_uom.id,
                                            'location_id' : self.location_id.id,
                                            'location_dest_id': self.location_dest_id.id,
                                     }))
#                 conditions based on unique serial number 
                if self.product_id != data.product_id :
                    raise UserError(_('Serial Number %s does not belong to product - "%s".') % (rec,self.product_id.name))  
            
            if  self.product_qty == self.quantity_done and self.move_line_nosuggest_ids.lot_id:
                    raise UserError(_('Serial Number Already Exist'))
                
            if self.move_line_ids:
                self.move_line_ids.unlink()
               
            self.move_line_nosuggest_ids = data_list
                     
        else :
            raise UserError("Invalid File! Please import the 'csv' file")  
#     view reference for line_ids
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')
        return {
            'name': _('Lot/Serial Number Details'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'stock.move',
            'res_id':self.id,
            'view_id':view.id,
            'views':[(view.id, 'form')],
            'target':'new',
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids,
                show_destination_location=self.location_dest_id.child_ids,
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity= self.state != 'done'
            ),
              }
        
# ref: serial number count
    def save(self):
        if self.product_qty < self.quantity_done:
            raise UserError('Serial number count is greater than the product quantity')
        return True
    
class ProductUoM(models.Model):
    _inherit = 'product.uom'
    
# ref: product unit of measure
    @api.multi
    def _compute_quantity(self, qty, to_unit, round=True, rounding_method='UP'):
        if not self:
            return qty
        self.ensure_one()
        amount = qty / self.factor
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = tools.float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
        return amount