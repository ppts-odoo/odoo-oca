from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CrmLeadProduct(models.Model):
    _name = 'crm.lead.product'
    
    product_id =  fields.Many2one('product.product',string='Product')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Ordered Qty',default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float(string='Unit Price')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    lead_id = fields.Many2one('crm.lead')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    lead_product_ids = fields.One2many('crm.lead.product','lead_id',string='Products For Quotation')

    def action_create_quotation(self):
        order_lines = []
        for line in self.lead_product_ids:
            order_lines.append((0,0,{'product_id': line.product_id.id,
                'name': line.description,
                'product_uom_qty':line.qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'tax_id':[(6, 0, line.tax_id.ids)]
            }))

        if self.partner_id:
            vals = ({
                'default_partner_id':self.partner_id.id,
                'default_team_id': self.team_id.id,
                'default_campaign_id': self.campaign_id.id,
                'default_medium_id': self.medium_id.id,
                'default_source_id': self.source_id.id,
                'default_opportunity_id': self.id,
                'default_order_line':order_lines,
            })
        else:
            raise UserError('In order to create sale order, Customer field should not be empty!')

        return {
            'name': "Create Sale Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'context': vals,
        }