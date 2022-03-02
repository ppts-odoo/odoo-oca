# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    apply_round_off = fields.Boolean('Apply round off',default = True)
    amount_round_off = fields.Float(compute='_amount_all',string='Round off',readonly=True)
   
    @api.depends('order_line.price_total','apply_round_off')
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
            if self.apply_round_off == True:
                amount_total = round(self.amount_total)
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
    
             
