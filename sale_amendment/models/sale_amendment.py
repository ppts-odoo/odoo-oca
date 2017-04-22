# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import odoo
from odoo import api, fields, models

class SaleAmendment(models.Model):
    _name = "sale.amendment"
    _description = "Sales Amendment"
    

    name = fields.Char('Quotation No', size=64,readonly=True)         
    quotation_date = fields.Date ('Quotation Date',readonly=True) 
    amendment_line = fields.One2many('sale.amendment.line', 'amendment_id', 'Amendment Lines')
    remark = fields.Char('Remarks', size=64)
    sale_amendment_id = fields.Many2one('sale.order', string='Amendment')
    amendment = fields.Integer('Amendment',  readonly = True)
    amount_untaxed = fields.Float('Untaxed Amount', digits=(16, 2), readonly = True)
    amount_tax = fields.Float('Taxes', digits=(16, 2), readonly = True)
    amount_total = fields.Float('Total', digits=(16, 2), readonly = True)                      
              
SaleAmendment()    
     

class SaleAmendmentLine(models.Model):
    _name = "sale.amendment.line"
    _description = "SaleS Amendment line item"
    
    amendment_id = fields.Many2one('sale.amendment', 'rev')  
    product_uom_qty = fields.Float('Quantity', digits=(16, 2))
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')		
    product_id = fields.Many2one('product.product', 'Product')           
    unit_price = fields.Float('Unit Price', digits=(16, 2),readonly=True)
    subtotal = fields.Float('Sub Total', digits=(16, 2),readonly=True)
    discount = fields.Float('Discount (%)', digits=(16, 2), readonly=True)    
           
SaleAmendmentLine()

