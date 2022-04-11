# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    opportunity_id = fields.Many2one('crm.lead',string='Products For Quotation')