from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round
from datetime import datetime
from dateutil.relativedelta import relativedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    
    
    @api.depends('origin')
    def _compute_reference_value(self):
        for value in self:
            sale_ids = self.env['sale.order'].search([('name','=',value.origin)])
#             print(sale_ids,'mrp')
            if sale_ids:
                value.sale_reference = sale_ids.name
            else:
                mrp_ids = self.env['mrp.production'].search([('name','=',value.origin)])
                value.sale_reference = mrp_ids.sale_reference                
#             print(value.sale_reference,'sale')
            
    @api.depends('name')       
    def _compute_reference_mo(self):
        for value in self:
            if value.state == 'draft':
                sale_ids = self.env['sale.order'].search([('name','=',value.origin)])
                print(sale_ids,'mrp')
                if sale_ids:
                    value.mrp_reference = value.name
#                     print(value.mrp_reference,'mrp_reference')
                                                              
                else:
                    mrp_ids = self.env['mrp.production'].search([('name','=',value.origin)])
                    value.mrp_reference = mrp_ids.mrp_reference
#                     print(value.mrp_reference,'MO')
                    
            if not value.origin:
                value.mrp_reference = value.name
                
            else:
                mrp_ids = self.env['mrp.production'].search([('name','=',value.mrp_reference)])
                for ele in mrp_ids:
                    value.mrp_reference = ele.mrp_reference
                print(value.mrp_reference,'MO')           
                    
    
    sale_reference = fields.Char('SO Reference',compute='_compute_reference_value',store = True)  
    mrp_reference = fields.Char('MO Reference',compute='_compute_reference_mo',store = True)
    

    

class Workorder(models.Model):    
    _inherit = 'mrp.workorder'
    
   
    sale_reference = fields.Char('SO Reference',related='production_id.sale_reference')  
    mrp_reference = fields.Char('MO Reference',related='production_id.mrp_reference')    
    
    
    