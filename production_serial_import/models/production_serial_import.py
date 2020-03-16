# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import csv
from StringIO import StringIO
import base64
import os
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
            #serial_raw = production.move_raw_ids.filtered(lambda x: x.product_id.tracking == 'serial')
            main_product_moves = production.move_finished_ids.filtered(lambda x: x.product_id.id == production.product_id.id)
            serial_finished = (production.product_id.tracking == 'serial')
            serial = bool(serial_finished)
#             if serial_finished:
#                 quantity = 1.0
#             else:
            quantity = production.product_qty - sum(main_product_moves.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0
            lines = []
            existing_lines = []
            for move in production.move_raw_ids.filtered(lambda x: (x.product_id.tracking != 'none') and x.state not in ('done', 'cancel')):
                if not move.move_lot_ids.filtered(lambda x: not x.lot_produced_id):
                    qty = quantity / move.bom_line_id.bom_id.product_qty * move.bom_line_id.product_qty
                    if move.product_id.tracking == 'serial':
                        while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                            lines.append({
                                'move_id': move.id,
                                'quantity': min(1,qty),
                                'quantity_done': 0.0,
                                'plus_visible': True,
                                'product_id': move.product_id.id,
                                'production_id': production.id,
                            })
                            qty -= 1
                    else:           
                        lines.append({
                            'move_id': move.id,
                            'quantity': qty,
                            'quantity_done': 0.0,
                            'plus_visible': True,
                            'product_id': move.product_id.id,
                            'production_id': production.id,
                        })
                else:
                    existing_lines += move.move_lot_ids.filtered(lambda x: not x.lot_produced_id).ids
            res['serial'] = serial
            res['production_id'] = production.id
            res['product_qty'] = quantity
            res['product_id'] = production.product_id.id
            res['product_uom_id'] = production.product_uom_id.id
            res['consume_line_ids'] = map(lambda x: (0,0,x), lines) + map(lambda x:(4, x), existing_lines)
        return res

    @api.multi
    def do_produce(self):
        # Nothing to do for lots since values are created using default data (stock.move.lots)
        moves = self.production_id.move_raw_ids
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_('You should at least produce some quantity'))
        for move in moves.filtered(lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel')):
            if move.unit_factor:
                for q in self.production_lot_ids:
                    move.quantity_done_store += q.quantity_done * move.unit_factor
        moves = self.production_id.move_finished_ids.filtered(lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel'))
        for move in moves:
            if move.product_id.id == self.production_id.product_id.id:
                move.quantity_done_store += quantity
            elif move.unit_factor:
                move.quantity_done_store += quantity * move.unit_factor
        self.check_finished_move_lots()
        if self.production_id.state == 'confirmed':
            self.production_id.state = 'progress'
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def check_finished_move_lots(self):
        lots = self.env['stock.move.lots']
        produce_move = self.production_id.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel'))
        if produce_move and produce_move.product_id.tracking != 'none':
            if produce_move.product_id.tracking == 'serial':
#             if not self.lot_id:
#                 raise UserError(_('You need to provide a lot for the finished product'))
                for move_line in self.production_lot_ids:
                    existing_move_lot = produce_move.move_lot_ids.filtered(lambda x: x.lot_id == move_line.lot_id.id)
                    if existing_move_lot:
                        for move_id in existing_move_lot:
                            if move_id:
                                move_id.quantity += move_line.quantity_done
                                move_id.quantity_done += move_line.quantity_done
                            else:
                                vals = {
                                    'move_id': produce_move.id,
                                    'product_id': produce_move.product_id.id,
                                    'production_id': self.production_id.id,
                                    'quantity': move_line.quantity_done,
                                    'quantity_done': move_line.quantity_done,
                                    'lot_id': move_line.lot_id.id,
                                }
                                lots.create(vals)
                    else:
                        vals = {
                            'move_id': produce_move.id,
                            'product_id': produce_move.product_id.id,
                            'production_id': self.production_id.id,
                            'quantity': move_line.quantity_done,
                            'quantity_done': move_line.quantity_done,
                            'lot_id': move_line.lot_id.id,
                        }
                        lots.create(vals)
                    for move in self.production_id.move_raw_ids:
                        for movelots in move.move_lot_ids.filtered(lambda x: not x.lot_produced_id):
                            if movelots.quantity_done and move_line.lot_id:
                                #Possibly the entire move is selected
                                remaining_qty = movelots.quantity - movelots.quantity_done
                                if remaining_qty > 0:
                                    new_move_lot = movelots.copy()
                                    new_move_lot.write({'quantity': movelots.quantity_done, 'lot_produced_id': move_line.lot_id.id})
                                    movelots.write({'quantity': remaining_qty, 'quantity_done': 0})
                                else:
                                    movelots.write({'lot_produced_id': move_line.lot_id.id})
            elif produce_move and produce_move.product_id.tracking != 'lot':
                if not self.lot_id:
                    raise UserError(_('You need to provide a lot for the finished product'))
                existing_move_lot = produce_move.move_lot_ids.filtered(lambda x: x.lot_id == self.lot_id)
                if existing_move_lot:
                    existing_move_lot.quantity += self.product_qty
                    existing_move_lot.quantity_done += self.product_qty
                else:
                    vals = {
                        'move_id': produce_move.id,
                        'product_id': produce_move.product_id.id,
                        'production_id': self.production_id.id,
                        'quantity': self.product_qty,
                        'quantity_done': self.product_qty,
                        'lot_id': self.lot_id.id,
                    }
                    lots.create(vals)
                for move in self.production_id.move_raw_ids:
                    for movelots in move.move_lot_ids.filtered(lambda x: not x.lot_produced_id):
                        if movelots.quantity_done and self.lot_id:
                            #Possibly the entire move is selected
                            remaining_qty = movelots.quantity - movelots.quantity_done
                            if remaining_qty > 0:
                                new_move_lot = movelots.copy()
                                new_move_lot.write({'quantity': movelots.quantity_done, 'lot_produced_id': self.lot_id.id})
                                movelots.write({'quantity': remaining_qty, 'quantity_done': 0})
                            else:
                                movelots.write({'lot_produced_id': self.lot_id.id})
        return True
    
    def read_validate_csv(self, csv_dict_reader):
        """Read the rows and check that the number of items in header line
        (which we know has no items with commas, so it cannot get screwed) matches the number
        of items in each row. If there is a mismatch, then raise an exception.
        Note: file that contains only the header is considered as invalid file.
        Returns list of rows.
        Args:
            csv_dict_reader - csv.DictReader
        Raises exceptions:
            csv.Error
        """
        res = []
        # self.check_model_fields(model_obj, csv_dict_reader.fieldnames)
        for row in csv_dict_reader:
            if len(row) != len(csv_dict_reader.fieldnames):
                raise csv.Error('Parsing failed: Header and row have different number of fields')
            # accumulate rows
            res.append(row)
        if not res:
            if len(csv_dict_reader.fieldnames):
                raise csv.Error('Parsing failed: File contains header only')
            else:
                # assume that the file is invalid
                raise csv.Error('Parsing failed: Invalid file')
        return res
    
    def read_lines(self,input_file):
        """Enumerate several most probable formats for csv.reader, first one is the same that
        is used for exporting stock picking objects. With each format, try to open the CSV-file
        and read the orders if the integrity check is passed successfully.
        Returns the list of move lines. Each move line is a dictionary
        Args:
            input_file - file object (StringIO)
        Raises exceptions:
            osv.except_osv
        """
        # define the list of CSV formats
        formats = [
                    # this format is used to export stock picking objects to CSV for fulfillment
                    # partners in stock_picking_out::ibood_csv_delivery() (ibood_docdata/delivery.py)
                    {'delimiter': ',', 'quoting': csv.QUOTE_MINIMAL, 'escapechar' : ';' },
                    # this format may be used if the CSV is edited by tools like LibreOffice
                    # (commas are escaped with backslashes)
                    {'delimiter': ',', 'quoting': csv.QUOTE_NONE,    'escapechar' : '\\'},
                    # just another version of the previous format
                    {'delimiter': ',', 'quoting': csv.QUOTE_MINIMAL, 'escapechar' : '\\'} ]
        # if the appropriate format will not be found afterward, save the error text that
        # will be obtained from parsing with the default format at iteration 0
        default_format_exception_text = ''
        for f in formats:
            # seek to start of file
            input_file.seek(0)
            # create dictionary reader and pass current format
            # turn strict mode on to raise exception csv.Error on bad CSV input
            csv_reader = csv.DictReader(input_file, strict = True, **f)
            try:
                lines = self.read_validate_csv(csv_reader)
                # check that each move line contains at least one valuable field
                for line in lines[:]:
                    for value in line.values():
                        if value and not(isinstance(value, basestring) and value.strip() == ''):
                            break
                    else:
                        # if all fields are None or string consisting of spaces, then remove
                        # such move line from the results
                        lines.remove(move_line)
                return lines
            except csv.Error as e:
                if f is formats[0]:
                    default_format_exception_text = str(e)
        # appropriate format not found, raise exception with previously saved error description
        raise UserError(_(default_format_exception_text))
    
#     importing "csv" file and appending the datas from file to order lines 
    @api.multi
    def input_file(self):
        if self.file_import:
            filename,FileExtension = os.path.splitext(self.file_name)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import the 'csv' file")
            data_list = []
            input_file = StringIO(base64.b64decode(self.file_import))
            input_ids = self.read_lines(input_file)
            for rec in input_ids:
                if 'Serial Number' not in rec:
                    raise UserError ('Row header name "Serial Number" is not found in CSV file')
                data = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id),('name','=',rec.get('Serial Number'))])
                data_list.append((0,0,{'lot_id':data.id,
                                       'quantity_done': 1.0
                                 }))
                if self.product_id != data.product_id :
                    raise UserError(_('Serial Number %s does not belong to product - "%s".') % (rec.get('Serial Number'),self.product_id.name))  
            if len(input_ids) > self.product_qty :
                raise UserError('Serial number count is greater than the product quantity')
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
    quantity_done = fields.Float('Done')
    production_lot_id = fields.Many2one('mrp.product.produce', 'produce')
    
class StockMoveLots(models.Model):
    _inherit = 'stock.move.lots'

    _sql_constraints = [
        ('uniq_lot_id', 'unique(move_id, lot_id)', 'You have already mentioned this lot in another line')]