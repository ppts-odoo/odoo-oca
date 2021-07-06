from odoo import models,fields,api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
        
    _inherit = "sale.order"
    
    #using cron send mail to user for quotation expiration details#    
    def _action_cron(self):
        order_ids = self.env['sale.order'].search([('state','=','draft')])
        ICPSudo = self.env['ir.config_parameter'].sudo()
        reminder_frequency = ICPSudo.get_param('sale.reminder_frequency')
        # print (reminder_frequency)        
        template_id = self.env.ref('quotation_expiry_reminder.product_expiration_mail_inherit')
        today = datetime.now().date()
        sale_order_detail_list = []
        email_list = []
        frequency=''
        count = 1
        for order_id in order_ids:
            if order_id.validity_date:
                if reminder_frequency == "one_week_before":
                    frequency =  "One week"
                    expiry_date = order_id.validity_date
                    print(expiry_date,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                    date_after_seven_days = datetime.strptime(str(expiry_date),"%Y-%m-%d") - relativedelta(days=7)
                    print(date_after_seven_days,'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
                    date_after_7_days = date_after_seven_days.date()
                    print(date_after_7_days,'cccccccccccccccccccccccccccccc')
                    if today == date_after_7_days:
                        print ("sent mail to user one week")
                        sale_order_details = {}
                        email_detail_dict = {}
                        sale_order_details['serial'] = count
                        sale_order_details['name'] = order_id.name
                        sale_order_details['partner_id'] = order_id.partner_id.name
                        sale_order_details['validity_date'] = order_id.validity_date
                        sale_order_details['amount_total'] = order_id.amount_total
                        email_detail_dict['email'] = order_id.partner_id.email
                        email_list.append(email_detail_dict)
                        count += 1
                        sale_order_detail_list.append(sale_order_details)
         
                elif reminder_frequency == "two_week_before":
                    frequency =  "Two weeks"
                    expiry_date = order_id.validity_date
                    date_after_seven_days = datetime.strptime(str(expiry_date),"%Y-%m-%d") - relativedelta(days=15)
                    date_after_7_days = date_after_seven_days.date()
                    if today == date_after_7_days:
                        print ("sent mail to user two weeks")
                        sale_order_details = {}
                        email_detail_dict = {}
                        sale_order_details['serial'] = count
                        sale_order_details['name'] = order_id.name
                        sale_order_details['partner_id'] = order_id.partner_id.name
                        sale_order_details['validity_date'] = order_id.validity_date
                        sale_order_details['amount_total'] = order_id.amount_total
                        email_detail_dict['email'] = order_id.partner_id.email
                        email_list.append(email_detail_dict)
                        count += 1
                        sale_order_detail_list.append(sale_order_details)
 
                elif reminder_frequency == "one_month_before":
                    frequency =  "One month"
                    expiry_date = order_id.validity_date
                    date_after_seven_days = datetime.strptime(str(expiry_date),"%Y-%m-%d") - relativedelta(days=30)
                    date_after_7_days = date_after_seven_days.date()
                    print(date_after_7_days,'tttetettetetetet')
                    if today == date_after_7_days:
                        print ("sent mail to user one month")
                        sale_order_details = {}
                        email_detail_dict = {}
                        sale_order_details['serial'] = count
                        sale_order_details['name'] = order_id.name
                        sale_order_details['partner_id'] = order_id.partner_id.name
                        sale_order_details['validity_date'] = order_id.validity_date
                        sale_order_details['amount_total'] = order_id.amount_total
                        email_detail_dict['email'] = order_id.partner_id.email
                        email_list.append(email_detail_dict)
                        count += 1
                        sale_order_detail_list.append(sale_order_details)
        if template_id:
            for line in email_list:
                template_id.with_context({'frequency':frequency,'sale_order_list': sale_order_detail_list,'email_to': line['email']}).send_mail(order_id.id,force_send=True)
            
            
            
            
            