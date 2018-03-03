from odoo import api,fields, models # alphabetically ordered
from odoo.exceptions import UserError



class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	_description = "Purchase Order"


	revision = fields.Integer(string='Amendment Revision')
	state = fields.Selection(selection_add=[('amendment', 'Amendment')])
	amendment_name = fields.Char('Order Reference',copy=True,readonly=True)
	current_amendment_id = fields.Many2one('purchase.order','Current Amendment',readonly=True,copy=True)
	old_amendment_ids = fields.One2many('purchase.order','current_amendment_id','Old Amendment',readonly=True,context={'active_test': False})

	@api.model
	def create(self, vals):
		if 'amendment_name' not in vals:
			if vals.get('name', 'New') == 'New':
				# sequence number with amendment number
				seq = self.env['ir.sequence']
				vals['name'] = seq.next_by_code('purchase.order') or '/'
			vals['amendment_name'] = vals['name']
		return super(PurchaseOrder, self).create(vals)

	
	@api.multi
	def button_draft(self):
		orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'amendment'])
		orders.write({
            'state': 'draft',
        })
		orders.mapped('order_line').write({'purchase_line_id': False})
	
	@api.multi
	def create_amendment(self):
		self.ensure_one()
		# Assign Form view before amendment 
		view_ref = self.env['ir.model.data'].get_object_reference('purchase','purchase_order_form')
		view_id = view_ref and view_ref[1] or False,
		self.with_context(new_purchase_amendment=True).copy()
		self.write({'state': 'draft'})
		self.order_line.write({'state': 'draft'})
		self.mapped('order_line').write(
		    {'purchase_line_id': True})
		return {
		    'type': 'ir.actions.act_window',
		    'name': ('Purchase Order'),
		    'res_model': 'sale.order',
		    'res_id': self.id,
		    'view_type': 'form',
		    'view_mode': 'form',
		    'view_id': view_id,
		    'target': 'current',
		    'nodestroy': True,
		}

	@api.returns('self', lambda value: value.id)
	@api.multi
	def copy(self, defaults=None):
		if not defaults:
			defaults = {}
		if self.env.context.get('new_purchase_amendment'):
			prev_name = self.name
			revno = self.revision 
			# Assign default values for views
			self.write({'revision': revno + 1,'name': '%s-%02d' % (self.amendment_name,revno + 1)})
			defaults.update({'name': prev_name,'revision': revno,'state': 'cancel','invoice_count': 0,'current_amendment_id': self.id,'amendment_name': self.amendment_name,})
		return super(PurchaseOrder, self).copy(defaults)
	
	def button_amend(self):
		for purchase in self: 
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
# 			amendment_values = {
# 					  'purchase_link_id': purchase.id,
# 					  'name': purchase.name,
# 					  'quotation_date': purchase.date_order,
# 					  'amendment': purchase.revision,
# 					  'amount_untaxed': purchase.amount_untaxed,
# 					  'amount_tax': purchase.amount_tax,
# 					  'amount_total': purchase.amount_total,
# 					  'currency_id': purchase.currency_id.id,
# 					  'amendment_date': datetime.today(),
# 					  'purchase_amendment_line': [],
# 				 }
# 			amendment_lines_values = []
# 			for i in purchase.order_line:
# 				amendment_lines_values.append((0, 0, {
# 						'product_id': i.product_id.id,
# 						'purchase_amendment_id': purchase.revision,
# 						'product_uom_qty': i.product_qty,
# 						'product_uom': i.product_uom.id,
# 						'unit_price': i.price_unit,
# 						'subtotal': i.price_subtotal,
# 				  }))
# 			amendment_values['purchase_amendment_line'] = amendment_lines_values
# 			amendment_obj.create(amendment_values)
# 			revision = self.revision + 1
# 		purchase.write({'state': 'amendment','revision': revision})
		self.button_draft()
		self.create_amendment()
		self.write({'state': 'amendment'})


PurchaseOrder()