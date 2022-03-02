# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import base64
import os
from datetime import datetime
from odoo.tools import float_compare
from odoo.tools import float_compare, float_round, float_is_zero


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
            if 'qty_producing' in fields:
                res['qty_producing'] = todo_quantity
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

    def do_produce(self):
        """ Save the current wizard and go back to the MO. """
        self.ensure_one()
        if self.production_lot_ids:
            self.with_context({'serial_import':True})._record_production()
        else:
            self._record_production()
        self._check_company()
        return {'type': 'ir.actions.act_window_close'}

    def _record_production(self):
        # Check all the product_produce line have a move id (the user can add product
        # to consume directly in the wizard)
        for line in self._workorder_line_ids():
            if not line.move_id:
                # Find move_id that would match
                if line.raw_product_produce_id:
                    moves = self.move_raw_ids
                else:
                    moves = self.move_finished_ids
                move_id = moves.filtered(lambda m: m.product_id == line.product_id and m.state not in ('done', 'cancel'))
                if not move_id:
                    # create a move to assign it to the line
                    if line.raw_product_produce_id:
                        values = {
                            'name': self.production_id.name,
                            'reference': self.production_id.name,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'location_id': self.production_id.location_src_id.id,
                            'location_dest_id': line.product_id.property_stock_production.id,
                            'raw_material_production_id': self.production_id.id,
                            'group_id': self.production_id.procurement_group_id.id,
                            'origin': self.production_id.name,
                            'state': 'confirmed',
                            'company_id': self.production_id.company_id.id,
                        }
                    else:
                        values = self.production_id._get_finished_move_value(line.product_id.id, 0, line.product_uom_id.id)
                    move_id = self.env['stock.move'].create(values)
                line.move_id = move_id.id

        # because of an ORM limitation (fields on transient models are not
        # recomputed by updates in non-transient models), the related fields on
        # this model are not recomputed by the creations above
        self.invalidate_cache(['move_raw_ids', 'move_finished_ids'])

        # Save product produce lines data into stock moves/move lines
        quantity = self.qty_producing
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified.") % self.product_id.display_name)
        self._update_finished_move()
        if not self.env.context.get('serial_import'):
            self._update_moves()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'date_start': datetime.now(),
            })

    def _update_finished_move(self):
        """ Update the finished move & move lines in order to set the finished
        product lot on it as well as the produced quantity. This method get the
        information either from the last workorder or from the Produce wizard."""

        production_move = self.production_id.move_finished_ids.filtered(
            lambda move: move.product_id == self.product_id and
                         move.state not in ('done', 'cancel')
        )
        if production_move and production_move.product_id.tracking != 'none':
            if not self.production_lot_ids:
                raise UserError(_('You need to provide a lot for the finished product.'))
            move_line = production_move.move_line_ids.filtered(
                lambda line: line.lot_id.id in self.production_lot_ids
            )
            if move_line:
                if self.product_id.tracking == 'serial':
                    raise UserError(_('You cannot produce the same serial number twice.'))
                move_line.product_uom_qty += self.qty_producing
                move_line.qty_done += self.qty_producing
            else:
                for mv in self.production_lot_ids:
                    location_dest_id = production_move.location_dest_id._get_putaway_strategy(self.product_id).id or production_move.location_dest_id.id
                    move_line.create({
                        'move_id': production_move.id,
                        'product_id': production_move.product_id.id,
                        'lot_id': mv.lot_id.id,
                        'product_uom_qty': mv.qty_done,
                        'product_uom_id': self.product_uom_id.id,
                        'qty_done': mv.qty_done,
                        'location_id': production_move.location_id.id,
                        'location_dest_id': location_dest_id,
                    })

                for line in self.production_id.move_raw_ids.move_line_ids:
                    reserved_qty = line.product_uom_qty / self.qty_producing
                    for mov in self.production_lot_ids:
                        rounding = line.product_uom_id.rounding
                        if float_compare(reserved_qty, line.product_uom_qty, precision_rounding=rounding) >= 0:
                            line.write({
                                'qty_done': reserved_qty,
                                'lot_produced_ids': mov.lot_id.ids,
                            })
                        else:
                            new_qty_reserved = line.product_uom_qty - reserved_qty
                            default = {
                                'product_uom_qty': new_qty_reserved,
                                'qty_done': new_qty_reserved,
                                'lot_produced_ids': mov.lot_id.ids,
                            }
                            line.copy(default=default)
                            line.with_context(bypass_reservation_update=True).write({
                                'product_uom_qty': new_qty_reserved,
                                'qty_done': 0
                            })
        else:
            rounding = production_move.product_uom.rounding
            production_move._set_quantity_done(
                float_round(self.qty_producing, precision_rounding=rounding)
            )


    def input_file(self):
        if self.file_import:
            file_value = self.file_import.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.file_name)
            if FileExtension != '.csv':
                raise UserError("Invalid File! Please import the 'csv' file")
            data_list = []
            input_file = base64.b64decode(file_value)
            lst = []
            for loop in input_file.decode("utf-8"):
                lst.append(loop)
            lsts = input_file.decode("utf-8").split("\n")
            if 'Serial Number' not in lsts[0]:
                raise UserError('Row header name "Serial Number" is not found in CSV file')
            lsts.pop(0)
            filter(None, lsts)
            result = list(filter(None, lsts))

            for vals in result:
                if vals:
                    data = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', 'ilike', vals.replace('\r', ''))])
                    data_list.append((0, 0, {'lot_id': data.id,
                                             'qty_done': 1
                                             }))
                    if self.product_id != data.product_id:
                        raise UserError(_('Serial Number %s does not belong to product - "%s".') % (str(vals), self.product_id.name))
            if len(result) > self.qty_producing:
                raise UserError('Serial number count is greater than the product quantity')
            lot_id_check = self.env['stock.move.line'].search([('lot_id', '=', data.id)])
            if lot_id_check:
                raise ValidationError('You have already mentioned this lot in another line')
            else:
                self.production_lot_ids = data_list

        else:
            raise UserError("Invalid File! Please import the 'csv' file")
        view = self.env.ref('mrp.view_mrp_product_produce_wizard')
        return {
            'name': _('Produce'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.product.produce',
            'res_id': self.id,
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
        }


class ProductionLot(models.TransientModel):
    _name = 'production.lot'

    lot_id = fields.Many2one('stock.production.lot', 'lot id')
    qty_done = fields.Float('Done')
    production_lot_id = fields.Many2one('mrp.product.produce', 'produce')
