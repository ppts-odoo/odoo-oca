# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            sale_obj = self.env['sale.order']
            order = sale_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
                return 'all'
        return 'delivered'

    advance_payment_method = fields.Selection([
        ('delivered', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)'),
        ('moredownpay', 'Down Payment (greater than Untaxed Amount)'),
    ], string='What do you want to invoice?', default=_get_advance_payment_method, required=True)


    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        inv_values ={}
        comments=''
        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
# Do not include tax based on down payment add tax with invoice
        inv_line={
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'account_analytic_id': order.project_id.id or False,
        }
# Check for down payment type and based on that inculde tax with invoice line
        if self.advance_payment_method != 'moredownpay':
            taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
            if order.fiscal_position_id and taxes:
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
            else:
                tax_ids = taxes.ids
            inv_line.update({'invoice_line_tax_ids': [(6, 0, tax_ids)]})

        for line in order.order_line:
            if line.product_id:
                print(line.product_id.name.encode('utf-8').lower())
                product_name = line.product_id.name.encode('utf-8').lower()
                if 'ventura' in product_name:
                    comments = """
Subject to Terms and Conditions of Sale
Always refer to our install guide
Concrete Collaborative Ventura overlay is a non-structural topping. Reflective cracks may appear due to vibration, substrate flexure or existing joints and cracks. Due to its cementitious nature, Ventura is not completely homogenous and variations to the finished floor should be expected. Micro-cracking in the surface should be expected.
"""
        if comments:
            inv_values.update({'comment': comments})
        inv_values.update({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, inv_line)],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            # Do not copy terms and condition to invoice
        })
        invoice = inv_obj.create(inv_values)
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        downpay_product_id = self.env['ir.values'].get_default('sale.config.settings', 'deposit_product_id_setting')
        remain_sale_amount=0
        downpay_total=0
        for s_line in sale_orders.order_line:
            if s_line.product_id.id == downpay_product_id:
#down pay has no order qty so price unit taken directly
                downpay_total +=s_line.price_unit
        remain_sale_amount=sale_orders.amount_total - downpay_total
# Validate down payment
        if self.advance_payment_method == 'fixed':
            if self.amount <= 0:
                raise UserError(_("Down payment amount should be greater than 0."))
            down_pay_amount = downpay_total+self.amount
            if self.amount > sale_orders.amount_untaxed:
                raise UserError(_("The value (down payment) entered is greater than untaxed amount of Sale Order."))
            if down_pay_amount > sale_orders.amount_untaxed:
                raise UserError(_("Advance amount received already please use the remaining sale untaxed amount."))

        if self.advance_payment_method == 'moredownpay':
            if self.amount <= 0:
                raise UserError(_("Down payment amount should be greater than 0."))
            if remain_sale_amount == 0:
                raise UserError(_("No more down payment applicable.  Already full value of Sales Order been received as down payment"))
            if self.amount > remain_sale_amount and remain_sale_amount != sale_orders.amount_total:
                raise UserError(_("Already partial down payment received. Value entered exceed the difference of already received down payment and the sales order."))
            if self.amount > sale_orders.amount_total:
                raise UserError(_("The value (down payment) entered is greater than the total value of Sales Order."))

        if self.advance_payment_method == 'delivered':
            sale_orders.action_invoice_create()
        elif self.advance_payment_method == 'all':
            sale_orders.action_invoice_create(final=True)
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.values'].sudo().set_default('sale.config.settings', 'deposit_product_id_setting', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
# If down pay done morethan untaxed amount do not use tax for down pay
                tax_ids=[]
                if self.advance_payment_method != 'moredownpay':
                    taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                    if order.fiscal_position_id and taxes:
                        tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                    else:
                        tax_ids = taxes.ids
                values={
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'product_uom_qty': 0.0,
                    'order_id': order.id,
                    'discount': 0.0,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                }
# Do update product tax based on down payment
                if tax_ids:
                    values.update({'tax_id': [(6, 0, tax_ids)],})
                else:
                    values.update({'tax_id': [], })
                so_line = sale_line_obj.create(values)

                self._create_invoice(order, so_line, amount)
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.deposit_account_id.id,
            'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
        }
