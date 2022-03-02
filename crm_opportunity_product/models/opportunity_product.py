# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class CrmLeadProduct(models.Model):
    _name = 'crm.lead.product'
    
    product_id =  fields.Many2one('product.product',string='Product')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Ordered Qty',default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure')
    price_unit = fields.Float(string='Unit Price')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    lead_id = fields.Many2one('crm.lead')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.lst_price

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    lead_product_ids = fields.One2many('crm.lead.product','lead_id',string='Products For Quotation')

    @api.multi
    def action_create_quotation(self):

        sale_obj=self.env['sale.order']
        sale_line_obj=self.env['sale.order.line']
        sale_id = sale_obj.create({
            'partner_id':self.partner_id.id,
            'team_id': self.team_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'opportunity_id': self.id
        })
        print('sale_idsale_idsale_id',sale_id,sale_id.id)
        for line in self.lead_product_ids:
            sale_line_obj.create({
                'order_id':sale_id.id,
                'product_id': line.product_id.id,
                'name': line.description,
                'product_uom_qty':line.qty,
                'price_unit': line.price_unit,
                'tax_id':[(6, 0, line.tax_id.ids)]

            })

        return True
    
    
    
    