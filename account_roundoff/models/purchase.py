# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit="purchase.order"

    apply_round_off = fields.Boolean('Apply round off', default=True)
    amount_round_off = fields.Monetary(string='Roundoff Amount', store=True, readonly=True, compute='_amount_all')
    is_enabled_roundoff = fields.Boolean('Apply Roundoff', default=lambda self: self.env["ir.config_parameter"].sudo().get_param("account.invoice_roundoff"))

    @api.onchange('is_enabled_roundoff')
    def onchange_is_enabled_roundoff(self):
        self._amount_all()

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0; amount_round_off = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
            if order.is_enabled_roundoff == True:
                amount_total = round(order.amount_total)
                amount_round_off = amount_total - order.amount_total
                order.update({
                    'amount_total': amount_total,
                    'amount_round_off': amount_round_off})
            else:
                if order.is_enabled_roundoff == False:
                    order.update({
                        'amount_untaxed': order.currency_id.round(amount_untaxed),
                        'amount_tax': order.currency_id.round(amount_tax),
                        'amount_total': amount_untaxed + amount_tax,
                    })
        return True