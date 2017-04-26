import odoo
from odoo import api, fields, models # alphabetically ordered
from odoo.exceptions import UserError
from datetime import datetime




class PurchaseOrder(models.Model):
	 _inherit = 'purchase.order'
	 _description = "Purchase Order"


	 revision = fields.Integer(string='Amendment Revision')
	 state = fields.Selection(selection_add=[('amendment', 'Amendment')])
	 po_amendment_ids = fields.One2many("purchase.amendment",'purchase_link_id',"Purchase Amendment Line")


	 def button_amend(self):
		for purchase in self: 
			pickings = self.env['stock.picking']
			amendment_obj = self.env['purchase.amendment']
			for picking_loop in purchase.picking_ids:
				if picking_loop.state == 'done':
					raise UserError('Unable to amend this purchase order, You must first cancel all receptions related to this purchase order.')
				else:
					picking_loop.filtered(lambda r: r.state != 'cancel').action_cancel()

			for invoice_loop in purchase.invoice_ids:
				if invoice_loop.state != 'draft':
					raise UserError('Unable to amend this purchase order, You must first cancel all Supplier Invoices related to this purchase order.')
				else:
					invoice_loop.filtered(lambda r: r.state != 'cancel').action_invoice_cancel()
			amendment_values = {
					  'purchase_link_id': purchase.id,
					  'name': purchase.name,
					  'quotation_date': purchase.date_order,
					  'amendment': purchase.revision,
					  'amount_untaxed': purchase.amount_untaxed,
					  'amount_tax': purchase.amount_tax,
					  'amount_total': purchase.amount_total,
					  'currency_id': purchase.currency_id.id,
					  'amendment_date': datetime.today(),
					  'purchase_amendment_line': [],
				 }
			amendment_lines_values = []
			for i in purchase.order_line:
				amendment_lines_values.append((0, 0, {
						'product_id': i.product_id.id,
						'purchase_amendment_id': purchase.revision,
						'product_uom_qty': i.product_qty,
						'product_uom': i.product_uom.id,
						'unit_price': i.price_unit,
						'subtotal': i.price_subtotal,
				  }))
			amendment_values['purchase_amendment_line'] = amendment_lines_values
			amendment_obj.create(amendment_values)
			revision = self.revision + 1
		purchase.write({'state': 'amendment','revision': revision})
		return True


	 
PurchaseOrder()