# -*- coding: utf-8 -*-
from odoo import api, models, _
import datetime
from calendar import month

class CrmTeam (models.Model):
    _inherit = "crm.team"
    
# function to view sale orders according to sale person     
#     @api.multi
    def view_sales(self):
        return {
                'name':_('Sale View'),
                'type':'ir.actions.act_window',
                'domain' : [('team_id.name', '=', self.name),('state','=','sale')],
                'context':{'search_default_sales_person': 1},
                'view_type':'form',
                'view_mode':'tree',
                'res_model':'sale.order',
                'res_id':self[0].id,
                'view_id':False,
                'views':[(self.env.ref('sale.view_order_tree').id or False, 'tree'), (self.env.ref('sale.view_order_form').id or False, 'form')],
                'target': 'current',
               }


# function to run in cron for triggering  mail of sale orders according to sale person on monthly basis.
    def run_scheduler(self):
        sale_team = self.env['crm.team'].search([])
        for saleperson in sale_team:
            data_list=[]
            for sale in saleperson.member_ids:
                content={}
                sale_order = self.env['sale.order'].search([('state','=','sale'),('team_id','=',saleperson.id),('user_id','=',sale.id)])
                for month in sale_order:
                    order_month = (month.date_order)
                    month_conv= datetime.datetime.strftime(order_month, "%Y-%m-%d %H:%M:%S")
                    if datetime.datetime.now().month ==order_month.month:
                        sale_count = len(sale_order)
                        lst = sale_order[0].user_id.name
                        sum_lst = [(loop.amount_total) for loop in sale_order]
                        content['saleperson']=lst
                        content['count']=sale_count
                        content['total']=sum(sum_lst)
                        content['sale_team']=saleperson.name
                data_list.append(content)
            if content:
               
                template_id_1 = self.env.ref('sale_tracker.example_email_template')
                if template_id_1:
                    template_id_1.with_context({'sale_order_list': data_list,'mail_ids':saleperson.user_id.login,'sale_team_name':saleperson.name}).send_mail(self.id, force_send=True)
        return True

            
# inherited sale order        
class SaleOrder (models.Model):
    _inherit = "sale.order"
    
