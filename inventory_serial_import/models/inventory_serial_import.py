# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import base64
import os
from odoo.tools.float_utils import float_compare, float_is_zero


class stock(models.Model):
    _inherit = "stock.move"

    file_import = fields.Binary("Import 'csv' File", help="*Import a list of lot/serial numbers from a csv file \n *Only csv files is allowed"
                                                          "\n *The csv file must contain a row header namely 'Serial Number'")
    file_name = fields.Char("file name")

    #     importing "csv" file and appending the datas from file to order lines
    
    def input_file(self):
        if self.file_import:
            file_value = self.file_import.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.file_name)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import the 'csv' file")
            data_list = []
            input_file = base64.b64decode(file_value)
            lst = []
            for loop in input_file.decode("utf-8").split("\n"):
                lst.append(loop)
            if 'Serial Number' not in lst[0]:
                raise UserError('Row header name "Serial Number" is not found in CSV file')
            lst_index = lst[0].replace('\r', '').split(',').index("Serial Number")
            lst.pop(0)
            for vals in lst:
                lst_r = []
                for value in vals.split(','):
                    lst_r.append(value)
                if vals and lst_r:
                    data = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', lst_r[lst_index].replace('\r', ''))])
                    data_list.append((0, 0, {'lot_id': data.id,
                                             'qty_done': 1,
                                             'product_uom_qty': 1,
                                             'product_uom_id': self.product_uom.id,
                                             'location_id': self.location_id.id,
                                             'location_dest_id': self.location_dest_id.id,
                                             'move_id': self.id,
                                             'product_id': self.product_id.id,
                                             'picking_id': self.picking_id.id
                                             }))
                #                 conditions based on unique serial number
                if self.product_id != data.product_id:
                    raise UserError(_('Serial Number %s does not belong to product - "%s".') % (str(vals), self.product_id.name))

            if len(list(filter(None, data_list))) > self.product_uom_qty:
                raise UserError('Serial number count is greater than the Initial Demand')

            if self.product_qty == self.quantity_done and self.move_line_nosuggest_ids.lot_id:
                raise UserError(_('Serial Number Already Exist'))

            if self.move_line_ids:
                self.move_line_ids.unlink()

            self.move_line_ids = data_list
            self.state = 'assigned'

        else:
            raise UserError("Invalid File! Please import the 'csv' file")
        #     view reference for line_ids
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
                show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done'
            ),
        }

    # ref: serial number count
    def save(self):
        if self.product_qty < self.quantity_done:
            raise UserError('Serial number count is greater than the product quantity')
        return True


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to reserve more products of %s than you have in stock.') % product_id.display_name)
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            # if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
            #     raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.') % product_id.display_name)
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
                break
        return reserved_quants

