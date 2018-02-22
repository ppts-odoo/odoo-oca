# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import csv
from StringIO import StringIO
import base64
import os

class stock(models.Model):   
    _inherit = "stock.pack.operation"
    
    file_import = fields.Binary("Import File", help="*Import a list of lot/serial numbers from a csv file \n *Only csv files is allowed"
                                                              "\n *The csv file must contain a row header namely 'Serial Number'")
    file_name = fields.Char("file name")
    
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
                                 }))
                if self.product_id != data.product_id :
                    raise UserError(_('Serial Number %s does not belong to product - "%s".') % (rec.get('Serial Number'),self.product_id.name))  
            if self.product_qty != len(input_ids):
                raise UserError('Serial number count is greater than the product quantity')
            self.pack_lot_ids = data_list
        else :
            raise UserError("Invalid File! Please import the 'csv' file")    
        return {
            'name': _('Lot/Serial Number Details'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'res_model':'stock.pack.operation',
            'res_id':self[0].id,
            'view_id':False,
            'views':[(self.env.ref('stock.view_pack_operation_lot_form').id or False, 'form')],
            'target':'new',
              }
