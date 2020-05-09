from odoo import api, fields, models,_
from odoo.exceptions import UserError, RedirectWarning

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class AccountMove(models.Model):
    _inherit ="account.move"

    is_1099 = fields.Boolean("1099")


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        warning = {}
        if self.partner_id:
            rec_account = self.partner_id.property_account_receivable_id
            pay_account = self.partner_id.property_account_payable_id
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
            p = self.partner_id
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn and p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s") % p.name,
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                    return {'warning': warning}
        for line in self.line_ids:
            line.partner_id = self.partner_id.commercial_partner_id
        if self.is_sale_document(include_receipts=True) and self.partner_id.property_payment_term_id:
            self.invoice_payment_term_id = self.partner_id.property_payment_term_id
        elif self.is_purchase_document(include_receipts=True) and self.partner_id.property_supplier_payment_term_id:
            self.invoice_payment_term_id = self.partner_id.property_supplier_payment_term_id

        self._compute_bank_partner_id()
        self.invoice_partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]
        self.is_1099 = self.partner_id.is_1099

        # Find the new fiscal position.
        delivery_partner_id = self._get_invoice_delivery_partner_id()
        new_fiscal_position_id = self.env['account.fiscal.position'].with_context(force_company=self.company_id.id).get_fiscal_position(
            self.partner_id.id, delivery_id=delivery_partner_id)
        self.fiscal_position_id = self.env['account.fiscal.position'].browse(new_fiscal_position_id)
        self._recompute_dynamic_lines()
        if warning:
            return {'warning': warning}



class account_payment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['communication'] = invoice['ref'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['amount_total']
            rec['is_1099'] = invoice['is_1099']
        return rec

    is_1099 = fields.Boolean("1099")


class Sent1099Forms(models.Model):
    _name = "sent.1099.forms"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner",string="Vendor")
    amount = fields.Float("Amount")
    file = fields.Binary("File")
    file_name = fields.Char("File Name")