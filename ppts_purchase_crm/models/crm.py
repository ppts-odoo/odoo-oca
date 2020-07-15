# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import Warning

class CrmLeadProduct(models.Model):
    _name = 'crm.lead.product'
     
    product_id =  fields.Many2one('product.product',string='Product',required=True)
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
            self.product_uom = self.product_id.uom_id.id

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    lead_type = fields.Selection([('sale','Sale'),('purchase','Purchase')],string='Lead Type',default='sale',required=True)
    lead_product_ids = fields.One2many('crm.lead.product','lead_id',string='Products For Quotation')
    purchase_amount_total= fields.Monetary(compute='_compute_purchase_amount_total', string="Sum of Orders", currency_field='company_currency')
    purchase_number = fields.Integer(compute='_compute_purchase_amount_total', string="Number of Quotations")
    po_order_ids = fields.One2many('purchase.order', 'opportunity_id', string='Orders')

    @api.depends('po_order_ids')
    def _compute_purchase_amount_total(self):
        for lead in self:
            total = 0.0
            nbr = 0
            company_currency = lead.company_currency or self.env.user.company_id.currency_id
            for order in lead.po_order_ids:
                if order.state in ('draft', 'sent'):
                    nbr += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    total += order.currency_id.compute(order.amount_untaxed, company_currency)
            lead.purchase_amount_total = total
            lead.purchase_number = nbr
 
    @api.multi
    def action_create_quotation(self):
        if not self.partner_id:
            raise Warning(_('Please enter the customer name.'))
            
        if self.lead_type == 'sale':
            view_id = self.env.ref('sale.view_order_form')
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
            if self.lead_product_ids:
                for line in self.lead_product_ids:
                    sale_line_obj.create({
                        'order_id':sale_id.id,
                        'product_id': line.product_id.id,
                        'name': line.description,
                        'product_uom_qty':line.qty,
                        'price_unit': line.price_unit,
                        'tax_id':[(6, 0, line.tax_id.ids)]
                    })
            return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'res_id':sale_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'nodestroy': True,
             }

        else:
            purchase_obj=self.env['purchase.order']
            view_id = self.env.ref('purchase.purchase_order_form')
            purchase_id = purchase_obj.create({
                'partner_id':self.partner_id.id,
                'opportunity_id': self.id
            })
            purchase_order_line = []  
            if self.lead_product_ids:         
                for line in self.lead_product_ids:
                    order_lines = (0,0,{
                        'product_id': line.product_id.id,
                        'name': line.description,
                        'product_qty':line.qty,
                        'product_uom': line.product_id.uom_po_id.id,
                        'price_unit': line.price_unit,
                        'date_planned':purchase_id.create_date,
                        'taxes_id':[(6, 0, line.tax_id.ids)],
                    })
                    purchase_order_line.append(order_lines)   
            purchase_id.order_line = purchase_order_line
            return {
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'res_id':purchase_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'nodestroy': True,
             }
 
        
     
     
     
     