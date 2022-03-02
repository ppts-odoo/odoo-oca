from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_roundoff = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    roundoff_account_id = fields.Many2one('account.account', string='Roundoff Account', implied_group='account.roundoff_account_id')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            roundoff_account_id=int(params.get_param('account.roundoff_account_id', default=False)) or False,
            invoice_roundoff=params.get_param('account.invoice_roundoff') or False,
        )
        return res

    def set_values(self):
        self.ensure_one()
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("account.roundoff_account_id", self.roundoff_account_id.id or False)
        self.env['ir.config_parameter'].sudo().set_param("account.invoice_roundoff", self.invoice_roundoff)


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    is_roundoff_line = fields.Boolean('Roundoff Line', default=False)

class AccountMove(models.Model):
    _inherit = 'account.move'

    round_off_value = fields.Monetary(string='Round off amount', store=True, readonly=True, compute='_compute_amount')
    round_off_amount = fields.Float(string='Round off Amount')
    rounded_total = fields.Monetary(string='Rounded Total', store=True, readonly=True, compute='_compute_amount')
    round_active = fields.Boolean('Enabled Roundoff', default=lambda self: self.env["ir.config_parameter"].sudo().get_param("account.invoice_roundoff"))

    # @api.model
    # def default_get(self, fields):
    #     res = super(AccountMove, self).default_get(fields)
    #     if self.env.context.get('active_model') == 'purchase.order':
    #         purchase = self.env['purchase.order'].browse(self.env.context.get('active_id'))
    #         if purchase.is_enabled_roundoff:
    #             account_id = int(self.env['ir.config_parameter'].sudo().get_param("account.roundoff_account_id"))
    #             if purchase.amount_round_off:
    #                 self.env['account.move.line'].new({
    #                     'name': 'Roundoff Amount',
    #                     'account_id': account_id,
    #                     'quantity': 1,
    #                     'price_unit': purchase.amount_round_off,
    #                     'display_type': False,
    #                     'is_roundoff_line': True,
    #                     'exclude_from_invoice_tab': False,
    #                     'is_rounding_line': False,
    #                     'predict_override_default_account': False,
    #                     'predict_from_name': False,
    #                     'move_id':self.id
    #                 })
    #     return res

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0;  total_untaxed_currency = 0.0; total_tax = 0.0; total_tax_currency = 0.0
            total_residual = 0.0; total_residual_currency = 0.0; total = 0.0; total_currency = 0.0;amount_round_off =0.00
            currencies = set()
            for line in move.line_ids:
                if line.is_roundoff_line == False:
                    if line.currency_id:
                        currencies.add(line.currency_id)
                    if move.is_invoice(include_receipts=True):
                        # === Invoices ===
                        if not line.exclude_from_invoice_tab:
                            # Untaxed amount.
                            total_untaxed += line.balance
                            total_untaxed_currency += line.amount_currency
                            total += line.balance
                            total_currency += line.amount_currency
                        elif line.tax_line_id:
                            # Tax amount.
                            total_tax += line.balance
                            total_tax_currency += line.amount_currency
                            total += line.balance
                            total_currency += line.amount_currency
                        elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                            # Residual amount.
                            total_residual += line.amount_residual
                            total_residual_currency += line.amount_residual_currency
                    else:
                        # === Miscellaneous journal entry ===
                        if line.debit:
                            total += line.balance
                            total_currency += line.amount_currency
            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            # Round off amoount updates
            if move.round_active and move.amount_total:
                amount_total = round((move.amount_total))
                amount_round_off = amount_total - move.amount_total
                move.round_off_value = amount_round_off
                move.round_off_amount = amount_round_off
                move.rounded_total = amount_total
                move.amount_total = amount_total
                move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            else:
                move.round_off_value = 0.00
                move.round_off_amount = 0.00
                move.rounded_total =0.00
            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual
            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'
            for record in move.invoice_line_ids:
                if record.is_roundoff_line == True and amount_round_off:
                    record.update({'price_unit': amount_round_off})
                    for lines in self.line_ids:
                        if lines.account_id.user_type_id.type in ('Receivable', 'receivable'):
                            lines.update({'debit': move.amount_total})
                            break
                        elif lines.account_id.user_type_id.type in ('Payable', 'payable'):
                            lines.update({'credit': move.amount_total})
                            break

    def _construct_values(self, account_id, accountoff_amount):
        values = [0, 0, {
            'name': 'Roundoff Amount',
            'account_id': account_id,
            'quantity': 1,
            'price_unit': accountoff_amount,
            'display_type': False,
            'is_roundoff_line': True,
            'exclude_from_invoice_tab': False,
            'is_rounding_line': False,
            'predict_override_default_account': False,
            'predict_from_name': False,
        }]
        return values

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if vals_list:
            if 'invoice_line_ids' in vals_list[0].keys():
                account_id = int(self.env['ir.config_parameter'].sudo().get_param("account.roundoff_account_id"))
                accountoff_amount = 0.00
                if self.env.context.get('active_id') and self.env.context.get('active_model') == 'sale.order':
                    sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
                    if sale and sale.is_enabled_roundoff:
                        accountoff_amount = sale.amount_round_off
                    if accountoff_amount:
                        values = self._construct_values(account_id, accountoff_amount)
                        vals_list[0]['invoice_line_ids'].append(values)
                else:
                    if vals_list[0].get('round_active') ==True and vals_list[0].get('round_off_amount'):
                        # If rounding amount is available, then update the total amount and add the roundoff value as new line.
                        account_id = int(self.env['ir.config_parameter'].sudo().get_param("account.roundoff_account_id"))
                        flag=False
                        for record in vals_list[0].get('line_ids'):
                            if record[2]['account_id']:
                                account = self.env['account.account'].browse(record[2]['account_id'])
                                # Update the values for the sale order
                                if account.user_type_id.type in ('Receivable', 'receivable'):
                                    if vals_list[0]['round_off_amount'] <0.0:
                                        total=abs(record[2]['price_unit']) - abs(vals_list[0]['round_off_amount'])
                                    else:
                                        total = abs(record[2]['price_unit']) + abs(vals_list[0]['round_off_amount'])
                                    record[2]['price_unit']=-total
                                    record[2]['debit'] = total
                                    flag=True
                                # Update the values for the purchase order
                                elif account.user_type_id.type in ('Payable', 'payable'):
                                    if vals_list[0]['round_off_amount'] < 0.0:
                                        total = abs(record[2]['price_unit']) - abs(vals_list[0]['round_off_amount'])
                                    else:
                                        total = abs(record[2]['price_unit']) + abs(vals_list[0]['round_off_amount'])
                                    record[2]['price_unit'] = -total
                                    record[2]['credit'] = total
                                    flag = True
                        if flag ==True:
                            values = self._construct_values(account_id, vals_list[0]['round_off_amount'])
                            vals_list[0]['line_ids'].append(values)
                            vals_list[0]['invoice_line_ids'].append(values)
            if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
                raise UserError(_('You cannot create a move already in the posted state. Please create a draft move and post it after.'))
            vals_list = self._move_autocomplete_invoice_lines_create(vals_list)
        return super(AccountMove, self).create(vals_list)