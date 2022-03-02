from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime
from odoo.http import request
from odoo.sql_db import TestCursor
from feedparser import base64


class VendorWizard(models.TransientModel):
    _name = "vendor.1099.form"

    year = fields.Selection([(num, str(num)) for num in range(((datetime.now().year) - 10), ((datetime.now().year) + 1))])
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(string="Total Amount",store=True,currency_field='currency_id')
    pdf_file = fields.Binary("1099 File")
    file_name = fields.Char("File Name")
    partner_id = fields.Many2one("res.partner",string="Vendor")
    success_msg = fields.Char("Message")
    warning_msg = fields.Char("Message")

    @api.onchange('year')
    def _onchange_partner_id(self):
        if self.year:
            self.success_msg=''
            self.warning_msg=''
            self.amount =0.0
            self.pdf_file=False
            self.file_name=''
            
    
    @api.multi
    def generate_1099(self):
        partner_br = self.env["res.partner"].browse(self.env.context.get('partner_id'))
        acc_payment_ids = self.env["account.payment"].search([('is_1099', '=', True),('partner_id','=',self.env.context.get('partner_id'))])

        if acc_payment_ids:
            amount = 0.0
            flag = False
            for line in acc_payment_ids:
                payment_year= datetime.strptime(line.payment_date, "%Y-%m-%d").date().year
                if payment_year == self.year:
                    amount += line.amount
                    self.amount = amount
                    report = self.env['ir.actions.report']._get_report_from_name("us_1099_form.report_1099")
                    pdf = report.with_context({'amount': amount,'year':self.year}).render_qweb_pdf([self.env.context.get('partner_id')], data={})[0]
                    self.pdf_file = base64.encodestring(pdf)
                    self.file_name = partner_br.name + "_1099 Form_" + str(self.year) +".pdf"
                    self.partner_id = self.env.context.get('partner_id')
                    self.warning_msg = ""
                    self.success_msg = ""
                    flag = True
                if not flag:
                    self.success_msg = ""
                    self.warning_msg = "No transaction was found for the selected year"
                    self.amount = 0.0
                    self.pdf_file = False

        view_id = self.env.ref('us_1099_form.view_1099_vendor_wizard').id
        return {
            'name': _('1099 Form'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vendor.1099.form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
        }

    @api.multi
    def send_1099(self):
        if self.pdf_file and self.file_name:
            try:
                template_id = self.env.ref('us_1099_form.template_send_1099')
            except ValueError:
                template_id = False
            if self.partner_id.email:
                template_id.write({'email_to': self.partner_id.email})
                template_id.with_context({'amount': self.amount}).send_mail(self.partner_id.id, force_send=True)
                vendor_data = {
                    'partner_id': self.partner_id.id,
                    'amount': self.amount,
                    'file': self.pdf_file,
                    'file_name': self.file_name,
                }
                self.env["sent.1099.forms"].create(vendor_data)

                self.warning_msg=''
                self.success_msg = "Mail has been sent successfully."
            else:
                raise UserError(_('Vendor does not have Email ID!'))
        else:
            self.amount = 0.0
            raise UserError(_('Please Generate 1099 form then click on send 1099!'))

        view_id = self.env.ref('us_1099_form.view_1099_vendor_wizard').id
        return {
            'name': _('1099 Form'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vendor.1099.form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
        }