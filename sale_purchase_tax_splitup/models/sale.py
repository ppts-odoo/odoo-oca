# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    sale_tax_line_ids = fields.One2many('sale.order.tax', 'sale_id', string='Tax Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    
    @api.onchange('order_line')
    def _onchange_order_line(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.sale_tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.sale_tax_line_ids = tax_lines
        return
    
#     @api.multi
    def compute_taxes(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        sale_tax = self.env['sale.order.tax']
        ctx = dict(self._context)
        for sale in self:
#             Delete non-manual tax lines
            self._cr.execute("DELETE FROM sale_order_tax WHERE sale_id=%s AND manual is False", (sale.id,))
            self.invalidate_cache()
 
            # Generate one tax line per tax, however many invoice lines it's applied to
            tax_grouped = sale.get_taxes_values()
            
            # Create new tax lines
            for tax in tax_grouped.values():
                sale_tax.create(tax)
 
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'order_line': []})
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or 'New'
        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        if any(line.tax_id for line in result.order_line) and not result.sale_tax_line_ids:
            result.compute_taxes()
        return result
    
#     @api.multi
    def button_dummy(self):
        res = super(SaleOrder, self).button_dummy()
        self.compute_taxes()
        return res
    
    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        tax_obj = self.env['account.tax']
        tax_br = tax_obj.browse(tax['id'])
        vals = {
            'sale_id':self.id,
            'name': tax_br.description or tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'sequence': tax['sequence'],
            'base': tax['base'],
            'manual': False,
            #'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] or False,
            'account_id': tax['account_id'],
        }
        return vals
    
#     @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.order_line:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price_unit, self.currency_id, line.product_uom_qty, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped
    
class SaleOrderTax(models.Model):
    _name = "sale.order.tax"
    _description = "Sale Tax"
    _order = 'sequence'

    def _compute_base_amount(self):
        tax_grouped = {}
        for sale in self.mapped('sale_id'):
            tax_grouped[sale.id] = sale.get_taxes_values()
        for tax in self:
            tax.base = 0.0
            if tax.tax_id:
                key = tax.tax_id.get_grouping_key({
                    'tax_id': tax.tax_id.id,
                    'account_id': tax.account_id.id,
                    'account_analytic_id': tax.account_analytic_id.id,
                })
                if tax.sale_id and key in tax_grouped[tax.sale_id.id]:
                    tax.base = tax_grouped[tax.sale_id.id][key]['base']
#                 else:
#                     raise Warning('Tax Base Amount not computable probably due to a change in an underlying tax (%s).', tax.tax_id.name)

    sale_id = fields.Many2one('sale.order', string='Sale', ondelete='cascade', index=True)
    name = fields.Char(string='Tax Description', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='Tax Account', required=True, domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')
    amount = fields.Monetary()
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice tax.")
    company_id = fields.Many2one('res.company', string='Company', related='account_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id', store=True, readonly=True)
    base = fields.Monetary(string='Base', compute='_compute_base_amount')
    
    
    
class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    def get_grouping_key(self, invoice_tax_val):
#         self.ensure_one()
        return str(invoice_tax_val['tax_id']) + '-' + \
               str(invoice_tax_val['account_id']) + '-' + \
               str(invoice_tax_val['account_analytic_id']) + '-' + \
               str(invoice_tax_val.get('analytic_tag_ids', []))
               
               
               
   