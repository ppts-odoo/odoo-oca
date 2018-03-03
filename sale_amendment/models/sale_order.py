from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Order"

    amendment_name = fields.Char('Order Reference',copy=True,readonly=True)
    state = fields.Selection(selection_add=[('amendment', 'Amendment')])
    current_amendment_id = fields.Many2one('sale.order','Current Amendment',readonly=True,copy=True)
    old_amendment_ids = fields.One2many('sale.order','current_amendment_id','Old Amendment',readonly=True,context={'active_test': False})
    amendment_no = fields.Integer('Amendment',copy=False)
    
    @api.model
    def create(self, vals):
        if 'amendment_name' not in vals:
            if vals.get('name', 'New') == 'New':
                # sequence number with amendment number
                seq = self.env['ir.sequence']
                vals['name'] = seq.next_by_code('sale.order') or '/'
            vals['amendment_name'] = vals['name']
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'amendment'])
        orders.write({
            'state': 'draft',
        })
        orders.mapped('order_line').write({'sale_line_id': False})
       
    @api.multi
    def create_amendment(self):
        self.ensure_one()
        # Assign Form view before amendment 
        view_ref = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_sale_amendment=True).copy()
        self.write({'state': 'draft'})
        self.order_line.write({'state': 'draft'})
        self.mapped('order_line').write(
            {'sale_line_id': True})
        return {
            'type': 'ir.actions.act_window',
            'name': ('Sales Order'),
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
        if self.env.context.get('new_sale_amendment'):
            prev_name = self.name
            revno = self.amendment_no 
            # Assign default values for views
            self.write({'amendment_no': revno + 1,'name': '%s-%02d' % (self.amendment_name,revno + 1)})
            defaults.update({'name': prev_name,'amendment_no': revno,'state': 'cancel','invoice_count': 0,'current_amendment_id': self.id,'amendment_name': self.amendment_name,})
        return super(SaleOrder, self).copy(defaults)

    def go_amendment(self):
        for sale in self:
            #Check delivery details status
            for pick in sale.picking_ids:
                if pick.state == 'done':
                    raise UserError('Unable to amend this sales order. You must first cancel all receptions related to this sales order.')
                else:
                    pick.filtered(lambda r: r.state != 'cancel').action_cancel()
            #Check invoice details status
            for inv in sale.invoice_ids:
                if inv.state == 'done' or inv.state == 'open' :
                    raise UserError('Unable to amend this sales order. You must first cancel all Customer Invoices related to this sales order.')
                else:
                    inv.filtered(lambda r: r.state != 'cancel').action_invoice_cancel()
        self.action_cancel()
        self.create_amendment()
        self.write({'state': 'amendment'})
           
SaleOrder()