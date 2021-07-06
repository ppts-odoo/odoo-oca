from odoo import models,fields,api,_
from datetime import datetime

class PurchaseOrder(models.Model):
        
    _inherit = "purchase.order"
    
    po_type = fields.Selection([('manual', 'Manual'),('from_sys', 'From System')], string='PO Type',required=True, copy=False, default='from_sys')

    #action cron send mail if purchase order created#    
#     @api.multi
    def _action_cron(self):
        order_ids = self.env['purchase.order'].search([('state','=','draft'),('po_type','=','from_sys')])
        ICPSudo = self.env['ir.config_parameter'].sudo()
        reorder_qty_mail_to = ICPSudo.get_param('purchase.reorder_qty_mail_to')
        if reorder_qty_mail_to:
            template_id = self.env.ref('reorder_qty_notification.reorder_qty_notification_inherit')
            purchase_order_detail_list = []
            count = 1
            order = False
            for order_id in order_ids:
                dt = datetime.strptime(str(order_id.date_order),'%Y-%m-%d %H:%M:%S')
                dt = datetime.strftime(dt,'%d-%m-%Y')
                for line_order in order_id.order_line:
                    purchase_order_details = {}
                    purchase_order_details['serial'] = count
                    purchase_order_details['name'] = order_id.name
                    purchase_order_details['partner_id'] = order_id.partner_id.name
                    purchase_order_details['date_order'] = dt
                    purchase_order_details['amount_total'] = order_id.amount_total
                    purchase_order_details['product_name'] = line_order.product_id.name
                    purchase_order_details['product_qty'] = line_order.product_qty
                    purchase_order_details['product_subtotal'] = line_order.price_subtotal
                    count += 1
                    purchase_order_detail_list.append(purchase_order_details)
                    order = order_id
            if template_id and order:
                template_id.with_context({'purchase_order_list': purchase_order_detail_list,'email_to': reorder_qty_mail_to}).send_mail(order.id,force_send=True)
    