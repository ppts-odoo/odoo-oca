from odoo import models, api, fields, _
import logging
_log = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    total_out_amount = fields.Float(compute='_compute_paid_customer_invoice',string='Amount',store=False)
    total_in_amount = fields.Float(compute='_compute_paid_supplier_invoice',string='Amount',store=False)
    sup_invoice_line_count = fields.Integer(string='Supplier Lines',compute='_supplier_invoice_count')
    cus_invoice_line_count = fields.Integer(string='Customer Lines',compute='_customer_invoice_count')
    
    @api.one
    def _compute_paid_customer_invoice(self):
        amount = 0
        amount_ref = 0
#         paid customer invoice total
        invoice_obj = self.env['account.invoice.line']
        invoice_lines = invoice_obj.search([('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', '=', 'out_invoice'),('invoice_id.state', '=', 'paid')])
        for line in invoice_lines:
            amount = amount + line.price_subtotal
#         if any refund customer invoice amount
        invoice_ref = invoice_obj.search([('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', '=', 'out_refund'),('invoice_id.state', '=', 'paid')])
        for line in invoice_ref:
            amount_ref = amount_ref + line.price_subtotal
        self.total_out_amount = amount - amount_ref
        
    @api.multi
    def _customer_invoice_count(self):
#         paid invoice line count
        for line in self:
            line.cus_invoice_line_count = self.env['account.invoice.line'].search_count(line._get_product_out_domain())
                
    @api.multi
    def _supplier_invoice_count(self):
#         paid invoice line count
        for line in self:
            line.sup_invoice_line_count = self.env['account.invoice.line'].search_count(line._get_product_in_domain())
        
    @api.one
    def _compute_paid_supplier_invoice(self):
        amount = 0
        amount_ref = 0
#        paid supplier invoice
        invoice_obj = self.env['account.invoice.line']
        invoice_lines = invoice_obj.search([('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', '=', 'in_invoice'),('invoice_id.state', '=', 'paid')])
        for line in invoice_lines:
            amount = amount + line.price_subtotal
#         if any refund customer invoice amount
        invoice_ref = invoice_obj.search([('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', '=', 'in_refund'),('invoice_id.state', '=', 'paid')])
        for line in invoice_ref:   
            amount_ref = amount_ref + line.price_subtotal
        self.total_in_amount = amount - amount_ref

    @api.multi
    def _get_product_out_domain(self):
#         customer invoice domain 
        domain = [('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', 'in', ['out_invoice', 'out_refund']),('invoice_id.state', '=', 'paid'),('invoice_id.state', '!=', 'cancel')]
        return domain
    
    @api.multi
    def _get_product_in_domain(self):
#         supplier invoice domain
        domain = [('product_id', 'in', self.product_variant_ids.ids),('invoice_id.type', 'in', ['in_invoice', 'in_refund']),('invoice_id.state', '=', 'paid'),('invoice_id.state', '!=', 'cancel')]
        return domain

    @api.multi
    def product_sup_invoice_view(self):
#         supplier invoice line view 
        tree_view = self.env.ref('product_invoice.account_invoice_line_tree')
        search_view = self.env.ref('product_invoice.search_account_invoice_line')
           
        return {
            'name': _('Supplier Invoice'),
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.line',
            'domain':(self._get_product_in_domain()),
            'views': [(tree_view.id, 'tree')],
            'view_mode': 'tree,form',
            'search_view_id': search_view.id,
            
             }

    @api.multi
    def product_cus_invoice_view(self):
#         customer invoice line view
        tree_view = self.env.ref('product_invoice.account_invoice_line_tree')
        search_view = self.env.ref('product_invoice.search_account_invoice_line')
        return {
            'name': _('Customer Invoice'),
            'res_model': 'account.invoice.line',
            'type': 'ir.actions.act_window',
            'views': [(tree_view.id, 'tree')],
            'domain':(self._get_product_out_domain()),
            'view_mode': 'tree,form',
            'search_view_id': search_view.id,
            'view_type': 'form',
             }

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
#     invoice view values related to invoice lines
    date_invoice = fields.Date(string='Date invoice',related='invoice_id.date_invoice',store=True,readonly=True)
    date_due = fields.Date(string='Date due',related='invoice_id.date_due',store=True,readonly=True)
     

