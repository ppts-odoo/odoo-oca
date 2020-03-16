# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, AccessError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    full_adjustment = fields.Boolean('Full Adjustment')
    advance_amount = fields.Float('Advance Amount')
    adjust_amount = fields.Float('Adjust Amount')
    balance = fields.Float('Balance', compute='_compute_balance')


# // Inherited Sale order
class SaleOrder(models.Model):
    _inherit = "sale.order"

# // Inherits the duplicate method to delete the down payment line items during duplication 
    @api.multi
    def copy(self, default=None):
        res = super(SaleOrder, self).copy(default)
        if default is None:
            default = {}
        downpay_product_id = self.env['ir.config_parameter'].get_param('sale.default_deposit_product_id')
        for line in res.order_line:
            if line.product_id.id == downpay_product_id:
                line.unlink()
        return res 
