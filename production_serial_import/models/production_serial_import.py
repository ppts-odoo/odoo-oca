# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
import base64
import os
from datetime import datetime
from odoo.tools import float_compare 

class MrpProductProduce(models.TransientModel):   
    _inherit = "mrp.product.produce"
    
    production_lot_ids = fields.One2many('production.lot', 'production_lot_id', string='Lot')
    file_import = fields.Binary("Import 'csv' File", help="*Import a list of lot/serial numbers from a csv file \n *Only csv files is allowed"
                                                              "\n *The csv file must contain a row header namely 'Serial Number'")
    file_name = fields.Char("file name")
    
    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            main_product_moves = production.move_finished_ids.filtered(lambda x: x.product_id.id == production.product_id.id)
            serial_finished = (production.product_id.tracking == 'serial')
#             if serial_finished:
#                 todo_quantity = 1.0
#             else:
            todo_quantity = production.product_qty - sum(main_product_moves.mapped('quantity_done'))
            todo_quantity = todo_quantity if (todo_quantity > 0) else 0
            if 'production_id' in fields:
                res['production_id'] = production.id
            if 'product_id' in fields:
                res['product_id'] = production.product_id.id
            if 'product_uom_id' in fields:
                res['product_uom_id'] = production.product_uom_id.id
            if 'serial' in fields:
                res['serial'] = bool(serial_finished)
            if 'product_qty' in fields:
                res['product_qty'] = todo_quantity
            if 'produce_line_ids' in fields:
                lines = []
                for move in production.move_raw_ids.filtered(lambda x: (x.product_id.tracking != 'none') and x.state not in ('done', 'cancel') and x.bom_line_id):
                    if not move.move_line_ids.filtered(lambda x: not x.lot_produced_id):
                        qty_to_consume = todo_quantity / move.bom_line_id.bom_id.product_qty * move.bom_line_id.product_qty
                        for move_line in move.move_line_ids:
                            if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                                break
                            if move_line.lot_produced_id or float_compare(move_line.product_uom_qty, move_line.qty_done, precision_rounding=move.product_uom.rounding) <= 0:
                                continue
                            to_consume_in_line = min(qty_to_consume, move_line.product_uom_qty)
                            lines.append({
                                'move_id': move.id,
                                'qty_to_consume': to_consume_in_line,
                                'qty_done': 0.0,
                                'lot_id': move_line.lot_id.id,
                                'product_uom_id': move.product_uom.id,
                                'product_id': move.product_id.id,
                            })
                            qty_to_consume -= to_consume_in_line
                        if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                            if move.product_id.tracking == 'serial':
                                while float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                                    lines.append({
                                        'move_id': move.id,
                                        'qty_to_consume': 1,
                                        'qty_done': 0.0,
                                        'product_uom_id': move.product_uom.id,
                                        'product_id': move.product_id.id,
                                    })
                                    qty_to_consume -= 1
                            else:
                                lines.append({
                                    'move_id': move.id,
                                    'qty_to_consume': qty_to_consume,
                                    'qty_done': 0.0,
                                    'product_uom_id': move.product_uom.id,
                                    'product_id': move.product_id.id,
                                })
                    
                    res['produce_line_ids'] = [(0, 0, x) for x in lines]
                    
        return res

    @api.multi
    def do_produce(self):
        # Nothing to do for lots since values are created using default data (stock.move.lots)
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified") % self.product_id.display_name)
        for move in self.production_id.move_raw_ids:
            # TODO currently not possible to guess if the user updated quantity by hand or automatically by the produce wizard.
            if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel') and move.unit_factor:
                if self.product_id.tracking != 'none':
                    for no_of_pro in self.production_lot_ids:
                        qty_to_add = no_of_pro.qty_done * move.unit_factor
                        move._generate_consumed_move_line(qty_to_add, self.lot_id)
                else:
                    move.qty_done += quantity * move.unit_factor
        for move in self.production_id.move_finished_ids:
            if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel'):
                if move.product_id.id == self.production_id.product_id.id:
                    move.qty_done += quantity
                elif move.unit_factor:
                    # byproducts handling
                    move.qty_done += quantity * move.unit_factor
        self.check_finished_move_lots()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def check_finished_move_lots(self):
        produce_move = self.production_id.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel'))
        if produce_move and produce_move.product_id.tracking != 'none':
            if produce_move.product_id.tracking == 'serial':
#                 if not self.lot_id:
#                     raise UserError(_('You need to provide a lot for the finished product'))
                for move_line in self.production_lot_ids:
                    existing_move_lot = produce_move.move_line_ids.filtered(lambda x: x.lot_id == move_line.lot_id.id)
                    if existing_move_lot:
                        for move_id in existing_move_lot:
                            if move_id:
                                move_id.quantity += move_line.qty_done
                                move_id.qty_done += move_line.qty_done
                            else:
                                vals = {
                                    'move_id': produce_move.id,
                                    'product_id': produce_move.product_id.id,
                                    'production_id': self.production_id.id,
                                    'quantity': self.product_qty ,
                                    'lot_id': move_line.lot_id.id,
                                    'product_uom_qty': self.product_qty,
                                    'product_uom_id': produce_move.product_uom.id,
                                    'qty_done': move_line.qty_done,
                                    'location_id': produce_move.location_id.id,
                                    'location_dest_id': produce_move.location_dest_id.id,

                                }
                                self.env['stock.move.line'].create(vals)
                    else:
                        vals = {
                            'move_id': produce_move.id,
                            'product_id': produce_move.product_id.id,
                            'production_id': self.production_id.id,
                            'quantity': move_line.qty_done,
                            'lot_id': move_line.lot_id.id,
                            'product_uom_qty': self.product_qty,
                            'product_uom_id': produce_move.product_uom.id,
                            'qty_done': move_line.qty_done,
                            'location_id': produce_move.location_id.id,
                            'location_dest_id': produce_move.location_dest_id.id,

                        }
                        self.env['stock.move.line'].create(vals)
                    for move in self.production_id.move_raw_ids:
                        for movelots in move.move_line_ids.filtered(lambda x: not x.lot_produced_id):
                            if movelots.qty_done and move_line.lot_id:
                                #Possibly the entire move is selected
                                remaining_qty = movelots.product_qty - movelots.qty_done
                                if remaining_qty > 0:
                                    new_move_lot = movelots.copy()
                                    new_move_lot.write({'quantity': movelots.qty_done, 'lot_produced_id': move_line.lot_id.id})
                                    movelots.write({'quantity': remaining_qty, 'qty_done': 0})
                                else:
                                    movelots.write({'lot_produced_id': move_line.lot_id.id})
            elif produce_move and produce_move.product_id.tracking != 'lot':
                if not self.lot_id:
                    raise UserError(_('You need to provide a lot for the finished product'))
                existing_move_line = produce_move.move_line_ids.filtered(lambda x: x.lot_id == self.lot_id)
                if existing_move_line:
                    if self.product_id.tracking == 'serial':
                        raise UserError(_('You cannot produce the same serial number twice.'))
                    existing_move_line.product_uom_qty += self.product_qty
                    existing_move_line.qty_done += self.product_qty
                else:
                    vals = {
                      'move_id': produce_move.id,
                      'product_id': produce_move.product_id.id,
                      'production_id': self.production_id.id,
                      'product_uom_qty': self.product_qty,
                      'product_uom_id': produce_move.product_uom.id,
                      'qty_done': move_line.qty_done,
                      'lot_id': self.lot_id.id,
                      'location_id': produce_move.location_id.id,
                      'location_dest_id': produce_move.location_dest_id.id,
                    }
                    self.env['stock.move.line'].create(vals)
    
            for pl in self.produce_line_ids:
                if pl.qty_done:
                    if not pl.lot_id:
                        raise UserError(_('Please enter a lot or serial number for %s !' % pl.product_id.name))
                    if not pl.move_id:
                        # Find move_id that would match
                        move_id = self.production_id.move_raw_ids.filtered(lambda x: x.product_id == pl.product_id and x.state not in ('done', 'cancel'))
                        if move_id:
                            pl.move_id = move_id
                        else:
                            # create a move and put it in there
                            order = self.production_id
                            pl.move_id = self.env['stock.move'].create({
                                        'name': order.name,
                                        'product_id': pl.product_id.id,
                                        'product_uom': pl.product_uom_id.id,
                                        'location_id': order.location_src_id.id,
                                        'location_dest_id': self.product_id.property_stock_production.id,
                                        'raw_material_production_id': order.id,
                                        'group_id': order.procurement_group_id.id,
                                        'origin': order.name,
                                        'state': 'confirmed'})
                    pl.move_id._generate_consumed_move_line(pl.qty_done, self.lot_id, lot=pl.lot_id)
        return True
    
   
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
            for vals in lsts:
                if vals:
                    data = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id),('name','ilike',vals.replace('\r',''))])
                    data_list.append((0,0,{'lot_id':data.id,
                                           'qty_done': 1
                                     }))
                    if self.product_id != data.product_id :
                        raise UserError(_('Serial Number %s does not belong to product - "%s".') % (str(vals),self.product_id.name))
            if len(lsts) > self.product_qty :
                raise UserError('Serial number count is greater than the product quantity')
            lot_id_check = self.env['stock.move.line'].search([('lot_id','=',data.id)])
            if lot_id_check:
                raise ValidationError('You have already mentioned this lot in another line')
            else:
                self.production_lot_ids = data_list
            
        else :
            raise UserError("Invalid File! Please import the 'csv' file")    
        view = self.env.ref('mrp.view_mrp_product_produce_wizard')
        return {
            'name': _('Produce'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'mrp.product.produce',
            'res_id':self.id,
            'view_id':view.id,
            'views':[(view.id, 'form')],
            'target':'new',
              }

class ProductionLot (models.TransientModel):
    _name = 'production.lot'
    
    lot_id = fields.Many2one('stock.production.lot','lot id') 
    qty_done = fields.Float('Done')
    production_lot_id = fields.Many2one('mrp.product.produce', 'produce')
  
