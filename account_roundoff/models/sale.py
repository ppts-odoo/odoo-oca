# -*- coding: utf-8 -*-

from odoo import fields,api,models,_
import math

class sale_order(models.Model):
    _inherit = 'sale.order'

    amount_round_off = fields.Float(compute='_amount_all',string='Round off',readonly=True)

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
            if self:
                amount_total = round(math.ceil(self.amount_total))
                amount_round_off = amount_total - self.amount_total
                order.update({
                    'amount_total': amount_total,
                    'amount_round_off': amount_round_off})
            else:
                amount_total = order.amount_total
                order.update({
                        'amount_total': amount_total,
                        'amount_round_off': 0.0
                    })
        return True   