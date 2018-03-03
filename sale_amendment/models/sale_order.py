import odoo
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Order"


    revision = fields.Integer(string='Revision')
    state = fields.Selection(selection_add=[('amendment', 'Amendment')])
    amendment_ids = fields.One2many('sale.amendment', 'sale_amendment_id', 'Amendments', readonly=True)


    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'amendment'])
        orders.write({
            'state': 'draft',
            'procurement_group_id': False,
        })
        orders.mapped('order_line').mapped('procurement_ids').write({'sale_line_id': False})


    @api.multi
    def create_amendment(self):
        for order in self:
            create_vals = {
                'sale_amendment_id': order.id,
                'name': order.name,
                'amendment': order.revision + 1,
                'amount_untaxed ': order.amount_untaxed,
                'amount_tax': order.amount_tax,
                'amount_total': order.amount_total,
                'quotation_date': order.date_order,
                'amendment_line': [],
            }
            line_data = []
            for i in order.order_line:
                line_data.append((0, 0, {
                    'product_id': i.product_id.id,
                    'product_uom_qty': i.product_uom_qty,
                    'product_uom': i.product_uom.id,
                    'unit_price': i.price_unit,
                    'discount': i.discount,
                    'subtotal': i.price_subtotal,
                }))
            create_vals['amendment_line'] = line_data
            self.env['sale.amendment'].create(create_vals)
        return True



    def go_amendment(self):
        proc_obj = self.env['procurement.order']
        picking_obj = self.env['stock.picking']
        procurement_obj = self.env['procurement.order']
        for sale in self:
            for pick in sale.picking_ids:
                if pick.state == 'done':
                    raise UserError('Unable to amend this sales order. You must first cancel all receptions related to this sales order.')
                else:
                    pick.filtered(lambda r: r.state != 'cancel').action_cancel()

            for inv in sale.invoice_ids:
                if inv.state not in ('cancel', 'draft'):
                    raise UserError('Unable to amend this sales order. You must first cancel all Customer Invoices related to this sales order.')
                else:
                    inv.filtered(lambda r: r.state != 'cancel').action_invoice_cancel()
            self.action_cancel()
            self.create_amendment()
        amendment_no = self.revision + 1
        self.write({'state': 'amendment', 'revision': amendment_no})
        return True


SaleOrder()