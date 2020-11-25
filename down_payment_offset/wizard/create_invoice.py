# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            # raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))


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


    # @api.depends('adjustable_down_payment_ids.adjust_amount_new')
    # def _compute_amount(self):
    #     # if self.adjustable_down_payment_ids:
    #     self.adjustable_amount = sum(line.adjust_amount_new for line in self.adjustable_down_payment_ids)

    @api.depends('adjustable_down_payment_ids.adjust_amount_new')
    def _compute_amount(self):
        for rec in self:
            amount = 0.0
            for line in rec.adjustable_down_payment_ids:
                amount += line.adjust_amount_new
            rec.update({
                'adjustable_amount': amount,
            })

    advance_payment_method = fields.Selection([
        ('delivered', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('adjust_down_payment', 'Invoiceable lines (adjust down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)'),
#         ('moredownpay', 'Down Payment (greater than Untaxed Amount)'),
    ], string='What do you want to invoice?', default=_get_advance_payment_method, required=True)
    adjustable_amount =  fields.Float('Adjustable Amount', digits=dp.get_precision('Account'), help="Adjustable amount from selected down payment.", compute='_compute_amount')
    adjustable_down_payment_ids = fields.One2many('adjustable.down.payment.line','sale_order_payment_inv_id','Down Payment To Be Adjusted')


    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        sale_obj = self.env['sale.order']
        order = sale_obj.browse(self._context.get('active_ids'))[0]
        downpay_product_id = self.env['ir.config_parameter'].get_param('sale.default_deposit_product_id')
        if self.advance_payment_method == 'adjust_down_payment':
            if order.order_line:
                vals = []
                invoiceable = False
                full_invoice = False
                val = {}
                for line in order.order_line:
                    
                    if line.product_id.id != downpay_product_id and line.product_id.type == 'product' and line.product_id.invoice_policy != 'delivery':
                        raise UserError(_('please change product invoice policy as Delivered Quantity for "%s".') %
                                (line.product_id.name))
                    if line.qty_to_invoice > 0:
                        invoiceable = True
                    if line.product_uom_qty != line.qty_delivered:
                        full_invoice = True

                    if line.product_id.id == self.product_id.id and line.qty_to_invoice < 0:
                        # val = {}
                        val = {'partner_id': order.partner_id.id,
                               'down_payment_reference': line.name,
                               'line_id': line.id,
                               'advance_amount': line.price_unit,
                               'advance_amount_new': line.price_unit,
                                 }
                        vals.append((0,0,val))

                        # val['partner_id'] = order.partner_id.id
                        # val['down_payment_reference'] = line.name
                        # val['line_id'] = line.id
                        # val['advance_amount'] = line.price_unit
                        # val['advance_amount_new'] = line.price_unit
                    # vals.append(val)
                if not full_invoice:
                    raise UserError(_('All products delivered. Please use deduct down payment option.'))

                if invoiceable:
                    self.adjustable_down_payment_ids = vals
                else:
                    raise UserError(_('There is no invoicable line.'))

            return {'value': {'amount': 0}}
        else:
            return super(SaleAdvancePaymentInv, self).onchange_advance_payment_method()
        return {}


#     @api.multi
    def create_invoices(self):
        sale_obj = self.env['sale.order']
        sale_order = sale_obj.browse(self._context.get('active_ids'))[0]
        if self.advance_payment_method == 'adjust_down_payment':
            if self.adjustable_amount == 0.0:
                raise ValidationError(_('Adjustable amount should be greated than 0.0'))
            inv_obj = self.env['account.move']
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            invoices = {}
            inv_values = {}
            references = {}
            downpay_total = 0
            downpay_product_id = self.env['ir.config_parameter'].get_param('sale.default_deposit_product_id')
            for s_line in sale_order.order_line:
                if s_line.product_id.id == downpay_product_id:
                    # down pay has no order qty so price unit taken directly
                    downpay_total += s_line.price_unit

            for order in sale_order:
                group_key = (order.partner_invoice_id.id, order.currency_id.id)
                vals = {}
                ll = []
                for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice != 0):
                    if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                        continue
                    if group_key not in invoices:
                        inv_data = order._prepare_invoice()
                        print('inv_data',inv_data)
                        invoice = inv_obj.create(inv_data)
                        print(';invoice',invoice)
                        references[invoice] = order
                        invoices[group_key] = invoice
                    elif group_key in invoices:
                        vals = {}
                        if order.name not in invoices[group_key].invoice_origin.split(', '):
                            vals['invoice_origin'] = invoices[group_key].invoice_origin + ', ' + order.name
                        if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                            vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                        invoices[group_key].write(vals)
                    if line.qty_to_invoice > 0:
                        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
                        if not account:
                            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

                        fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
                        if fpos:
                            account = fpos.map_account(account)
                #         inv_line={
                #                 'name': 'Draft Invoice',
                # #                 'invoice_origin': order.name,
                # #                 'analytic_account_id': account_id,
                #                 'price_unit': line.price_unit,
                #                 'quantity': 1.0,
                #                 'discount': 0.0,
                #                 'product_uom_id': line.product_id.uom_id.id,
                #                 'product_id': line.product_id.id,
                #                 'account_id': account.id,
                #                 'sale_line_ids': [(6, 0, [line.id])],
                # #                 'account_analytic_id': order.project_id.id or False,
                #         }
                #         print('inv_line222222222222',inv_line)
                # # Check for down payment type and based on that inculde tax with invoice line
                # #         if self.advance_payment_method != 'moredownpay':
                # #             taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                # #             if order.fiscal_position_id and taxes:
                # #                 tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                # #             else:
                # #                 tax_ids = taxes.ids
                # #             inv_line.update({'tax_ids': [(6, 0, tax_ids)]})

                #         inv_values.update({
                #             # 'name': order.client_order_ref or order.name,
                #             'name': 'Draft Invoice',
                #             'invoice_origin': order.name,
                #             'type': 'out_invoice',
                # #             'reference': False,
                # #             'account_id': order.partner_id.property_account_receivable_id.id,
                #             'partner_id': order.partner_invoice_id.id,
                #             'partner_shipping_id': order.partner_shipping_id.id,
                #             'invoice_line_ids': [(0, 0, inv_line)],
                #             'currency_id': order.pricelist_id.currency_id.id,
                #             'invoice_payment_term_id': order.payment_term_id.id,
                #             'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                #             'team_id': order.team_id.id,
                #             'user_id': order.user_id.id,
                #             # Do not copy terms and condition to invoice
                #         })
                #         print('inv_values33333333333333333',inv_values)
                #         invoice = inv_obj.create(inv_values)

                        """
                        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
                        (refund).

                        :param invoice_id: integer
                        :param qty: float quantity to invoice
                        """
                        qty = line.qty_to_invoice

                        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                        if not float_is_zero(qty, precision_digits=precision):
                            self.ensure_one()
                            res = {}
                            account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
                            if not account:
                                raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                                    (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

                            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
                            if fpos:
                                account = fpos.map_account(account)

                            vals = {
                                'name': line.name,
                                # 'sequence': line.sequence,
    #                                 'invoice_origin': line.order_id.name,
    #                                 'analytic_account_id': account.id,
                                'price_unit': line.price_unit,
                                'quantity': qty,
                                'discount': line.discount,
                                'product_uom_id': line.product_uom.id,
                                'product_id': line.product_id.id or False,
                                'account_id': account.id,
                                'move_id': invoice.id,
                                'sale_line_ids': [(6, 0, [line.id])]
                                # 'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
                                # 'tax_ids': [(6, 0, line.tax_id.ids)],
    #                                 'analytic_account_id': line.order_id.project_id.id,
                                # 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                            }
                            # vals.update({'move_id': invoice.id})
                            
                            # vals.update({'move_id': invoice.id, 'sale_line_ids': [(6, 0, [line.id])]})
                            print('vals',vals)
                            self.env['account.move.line'].create(vals)
                #         print('vals++++++++++',vals)
                #         ll.append(vals)
                # print('vals++++++11111111111++++',ll)
                # for lll in ll:
                #     line_ss =  self.env['account.move.line'].create(lll)
                #     print('----------------line_ss',line_ss)
                                       
                if references.get(invoices.get(group_key)):
                    if order not in references[invoices[group_key]]:
                        references[invoice] = references[invoice] | order
            if invoice.id and self.adjustable_down_payment_ids:
                for adjustable_down_payment_id in self.adjustable_down_payment_ids:
                    if adjustable_down_payment_id.adjust_amount_new > 0:
                        line = adjustable_down_payment_id.line_id
                        if line.product_id.id != downpay_product_id  and line.product_id.type == 'product' and line.product_id.invoice_policy != 'delivery':
                            raise UserError(_('please change product invoice policy as Delivered Quantity for "%s".') %
                                    (line.product_id.name))

                        if line.price_unit == adjustable_down_payment_id.adjust_amount_new:
                           
                            line = adjustable_down_payment_id.line_id
                            qty = line.qty_to_invoice

                            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                            if not float_is_zero(qty, precision_digits=precision):
                                self.ensure_one()
                                res = {}
                                account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
                                if not account:
                                    raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                                        (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

                                fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
                                if fpos:
                                    account = fpos.map_account(account)

                                vals = {
                                    'name': line.name,
                                    'sequence': line.sequence,
#                                     'invoice_origin': line.order_id.name,
#                                     'analytic_account_id': account.id,
                                    'price_unit': line.price_unit,
                                    'quantity': qty,
                                    'discount': line.discount,
                                    'product_uom_id': line.product_uom.id,
                                    'product_id': line.product_id.id or False,
                                    'account_id': account.id,
                                    # 'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
                                    'tax_ids': [(6, 0, line.tax_id.ids)],
                                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                                }
                                vals.update({'move_id': invoice.id, 'sale_line_ids': [(6, 0, [line.id])]})
                                self.env['account.move.line'].create(vals)
                        else:
                            line = adjustable_down_payment_id.line_id
                            qty = line.qty_to_invoice
                            
                            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                            if not float_is_zero(qty, precision_digits=precision):
                                self.ensure_one()
                                res = {}
                                account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
                                if not account:
                                    raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                                        (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

                                fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
                                if fpos:
                                    account = fpos.map_account(account)

                                vals = {
                                    'name': line.name,
                                    'sequence': line.sequence,
#                                     'invoice_origin': line.order_id.name,
#                                     'analytic_account_id': account.id,
                                    'price_unit': line.price_unit,
                                    'quantity': qty,
                                    'discount': line.discount,
                                    'product_uom_id': line.product_uom.id,
                                    'product_id': line.product_id.id or False,
                                    'account_id': account.id,
                                    # 'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
                                    'tax_ids': [(6, 0, line.tax_id.ids)],
#                                     'account_analytic_id': line.order_id.project_id.id,
                                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                                }
                                vals.update({'invoice_id': invoice.id, 'sale_line_ids': [(6, 0, [line.id])]})
                                self.env['account.move.line'].create(vals)
                                sale_vals = {
                                    'name': "Remaining of "+line.name,
                                    'product_id': int(downpay_product_id),
                                    'price_unit': line.price_unit - adjustable_down_payment_id.adjust_amount_new,
                                    'quantity': qty,
                                    'product_uom_qty': 0
                                }
                                sale_vals.update({'order_id': line.order_id.id})
                                return_line = self.env['sale.order.line'].create(sale_vals)

                                return_vals = {
                                    'name': "Remaining of "+line.name,
                                    'sequence': line.sequence,
#                                     'invoice_origin': line.order_id.name,
#                                     'analytic_account_id': account.id,
                                    'price_unit': line.price_unit - adjustable_down_payment_id.adjust_amount_new,
                                    'quantity': -(qty),
                                    'discount': line.discount,
                                    'product_uom_id': line.product_uom.id,
                                    'product_id': line.product_id.id or False,
                                    'account_id': account.id,
                                    # 'layout_category_id': line.layout_category_id and line.layout_category_id.id or False,
                                    'tax_ids': [(6, 0, line.tax_id.ids)],
                                    'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                                }
                                return_vals.update({'invoice_id': invoice.id, 'sale_line_ids': [(6, 0, [return_line.id])]})
                                self.env['account.move.line'].create(return_vals)

            if not invoices:
                raise UserError(_('There is no invoicable line.'))

            for invoice in invoices.values():
                if not invoice.invoice_line_ids:
                    raise UserError(_('There is no invoicable line.'))
                # If invoice is negative, do a refund invoice instead
                # Downpayment done morethan sale untaxed amount so do not inculd tax and do not make refund
                if sale_order.amount_untaxed > downpay_total:
                    if invoice.amount_untaxed < 0:
                        invoice.type = 'out_refund'
                        for line in invoice.invoice_line_ids:
                            line.quantity = -line.quantity
                # Use additional field helper function (for account extensions)
                # for line in invoice.invoice_line_ids:
                #     line._set_additional_fields(invoice)
                # Necessary to force computation of taxes. In account_invoice, they are triggered
                # by onchanges, which are not triggered when doing a create.
#                 invoice.compute_taxes()
                invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'invoice_origin': references[invoice]},
                    subtype_id=self.env.ref('mail.mt_note').id)
            # return [inv.id for inv in invoices.values()]
            if self._context.get('open_invoices', False):
                return sale_order.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()


class AdjustableDownPaymentLine(models.TransientModel):
    _name = 'adjustable.down.payment.line'

    @api.depends('advance_amount','adjust_amount_new')
    def _compute_balance(self):
        for rec in self:
            balance = rec.advance_amount_new  - rec.adjust_amount_new
            if balance < 0:
                raise UserError(
                    _('Balance amount should not be lesser than 0'))
            rec.balance = balance

    @api.onchange('full_adjustment')
    def _onchange_full_adjustment(self):
        if self.full_adjustment == True:
            self.adjust_amount = self.advance_amount 
            self.adjust_amount_new = self.advance_amount 
        else:
            self.adjust_amount = 0.0
            self.adjust_amount_new = 0.0
        return {}
    
    @api.onchange('adjust_amount')
    def _onchange_adjust_amount(self):
        if self.adjust_amount:
            self.adjust_amount_new  = self.adjust_amount

#     @api.one
    @api.constrains('balance')
    def _check_percent(self):
        if self.balance < 0:
            raise ValidationError(_('Balance amount should not be lesser than 0'))

    sale_order_payment_inv_id = fields.Many2one('sale.advance.payment.inv')
    partner_id = fields.Many2one('res.partner','Partner')
    down_payment_reference = fields.Char('Down Payment Reference')
    full_adjustment = fields.Boolean('Full Adjustment')
    advance_amount = fields.Float('Advance Amount')
    advance_amount_new = fields.Float('Advance Amount')
    adjust_amount = fields.Float('Adjust Amount')
    adjust_amount_new = fields.Float('Adjust Amount')
    balance = fields.Float('Balance', compute='_compute_balance')
    line_id = fields.Many2one('sale.order.line')

