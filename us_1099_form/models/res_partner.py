from odoo import api, fields, models,_

class Partner(models.Model):
    _inherit = "res.partner"

    is_1099 = fields.Boolean("1099")


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    def _prepare_invoice_values(self, order, name, amount, so_line):
    	invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
    	if order.partner_id.is_1099:
    		invoice_vals['is_1099'] = True
    	return invoice_vals

