import odoo
from odoo import api, fields, models # alphabetically ordered


class PurchaseAmendment(models.Model):
    _name = "purchase.amendment"
    _description = "Purchase Amendment"

    name = fields.Char('Purchase Order', size=64, readonly=True)
    quotation_date = fields.Date('Purchase Order Date', readonly=True)
    amendment_date = fields.Date('Amendment Date', readonly=True)
    purchase_amendment_line = fields.One2many('purchase.amendment.line', 'purchase_amendment_id',
                                               'amendment Lines', readonly=True)
    remark = fields.Char('Remarks', size=64)
    purchase_link_id = fields.Many2one('purchase.order', 'link')
    amendment = fields.Float('Amendment', digits=(16, 0), readonly=True)
    amount_untaxed = fields.Float('Untaxed Amount', digits=(16, 2), readonly=True)
    amount_tax = fields.Float('Taxes', digits=(16, 2), readonly=True)
    amount_total = fields.Float('Total', digits=(16, 2), readonly=True)
    add_disc = fields.Float('Additional Discount(%)', digits=(16, 2), readonly=True)
    add_disc_amt = fields.Float('Additional Discount Amt', digits=(16, 2), readonly=True)
    amount_net = fields.Float('Net Amount', digits=(16, 2), readonly=True)
    currency_id = fields.Many2one('res.currency',string="Currency", readonly=True)


PurchaseAmendment()


class PurchaseAmendmentLine(models.Model):
    _name = "purchase.amendment.line"
    _description = "Purchase amendment line item"

    purchase_amendment_id = fields.Many2one('purchase.amendment', 'rev')
    product_uom_qty = fields.Float('Quantity', digits=(16, 2))
    product_uom = fields.Many2one('product.uom', 'Unit of Measure ')
    product_id = fields.Many2one('product.product', 'Product')
    unit_price = fields.Float('Unit Price', digits=(16, 2), readonly=True)
    subtotal = fields.Float('Sub Total', digits=(16, 2), readonly=True)
    discount = fields.Float('Discount (%)', digits=(16, 2), readonly=True)
    


PurchaseAmendmentLine()