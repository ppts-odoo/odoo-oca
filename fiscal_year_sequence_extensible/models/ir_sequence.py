# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz
from odoo.exceptions import UserError
from odoo.addons.base.ir import ir_sequence

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    
    def _get_prefix_suffix(self, prefix=False, suffix=False):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if self._context.get('ir_sequence_date'):
                effective_date = datetime.strptime(self._context.get('ir_sequence_date'), '%Y-%m-%d')
            if self._context.get('ir_sequence_date_range'):
                range_date = datetime.strptime(self._context.get('ir_sequence_date_range'), '%Y-%m-%d')

            sequences = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, format in sequences.items():
                res[key] = effective_date.strftime(format)
                res['range_' + key] = range_date.strftime(format)
                res['current_' + key] = now.strftime(format)
                
            res.update({'prefix':prefix if prefix else "",'suffix':suffix if suffix else ""})
            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % (self.get('name')))
        return interpolated_prefix, interpolated_suffix
    
    def get_next_char(self, number_next, prefix=False, suffix=False):
        interpolated_prefix, interpolated_suffix = self._get_prefix_suffix(prefix, suffix)
        return interpolated_prefix + '%%0%sd' % self.padding % number_next + interpolated_suffix

class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'
 
    prefix = fields.Char(help="Prefix value of the record for the sequence")
    suffix = fields.Char(help="Suffix value of the record for the sequence")
    
    def _next(self):
        if self.sequence_id.implementation == 'standard':
            number_next = ir_sequence._select_nextval(self._cr, 'ir_sequence_%03d_%03d' % (self.sequence_id.id, self.id))
        else:
            number_next = ir_sequence._update_nogap(self, self.sequence_id.number_increment)
            
        return self.sequence_id.get_next_char(number_next, self.prefix, self.suffix)
    
