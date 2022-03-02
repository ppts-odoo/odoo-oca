from odoo import api, fields, models
from datetime import datetime


class Partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _get_total_value(self, name):
        amount = 0.0
        if self._context.get('amount'):
            amount = self._context.get('amount')
        else:
            payment_line = self.env["account.payment"].search([('partner_id','=',self.id),('is_1099','=',True)])
            if payment_line:
                for line in payment_line:
                    amount +=line.amount
        return amount

    @api.multi
    def _get_year(self, name):
        year = datetime.now().year
        if self._context.get('year'):
            year = self._context.get('year')
        return year


