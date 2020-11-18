# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class SaleOrderLine(models.Model):   
    _inherit = "sale.order.line"
    
    order_ref = fields.Char('Order Reference',related='order_id.name')   
    customer_id = fields.Many2one('res.partner',related='order_id.partner_id')


