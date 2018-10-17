from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime
from feedparser import base64


class WizardLine(models.TransientModel):
    _name = "wizard.line"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner",string="Vendor")
    amount = fields.Float("Amount")
    select = fields.Boolean("Select")
    acc_mail_id = fields.Many2one("acc.mail.wizard")
    file = fields.Binary("File")
    file_name = fields.Char("File Name")

class AccountMailWizard(models.TransientModel):
    _name ="acc.mail.wizard"

    year_from = fields.Selection([(num, str(num)) for num in range(((datetime.now().year) - 10), ((datetime.now().year) + 1))], string="Year From")
    year_to = fields.Selection([(num, str(num)) for num in range(((datetime.now().year) - 10), ((datetime.now().year) + 1))], string="To")
    vendor_ids = fields.One2many("wizard.line","acc_mail_id", string="Vendors")
    select_all = fields.Boolean("Select All")

    @api.onchange('year_from','year_to')
    def _onchange_year(self):
        self.vendor_ids.unlink()

    @api.onchange('select_all')
    def _onchange_select_all(self):
        if self.vendor_ids:
            if self.select_all:
                for line in self.vendor_ids:
                    line.select = True
            else:
                for line in self.vendor_ids:
                    line.select = False

    @api.multi
    def find_vendors(self):
        if self.year_from > self.year_to:
            raise UserError(_("'Date from' should be lesser than 'Date To'"))
        if self.vendor_ids:
            self.vendor_ids.unlink()
        acc_payment_ids = self.env["account.payment"].search([('is_1099','=',True)])
        vendor_data =[]
        exist_vendor = []
        if acc_payment_ids:
            for line in acc_payment_ids:
                payment_year = datetime.strptime(line.payment_date, "%Y-%m-%d").date().year
                if payment_year >= self.year_from and payment_year <= self.year_to:
                    if line.partner_id.id in exist_vendor:
                        for vendor in vendor_data:
                            if vendor[2]['partner_id'] == line.partner_id.id:
                                vendor[2]['amount'] += line.amount
                        if line.partner_id.id not in exist_vendor:
                            exist_vendor.append(line.partner_id.id)
                    else:
                        report = self.env['ir.actions.report']._get_report_from_name("us_1099_form.report_1099")
                        pdf = report.with_context({'amount': line.amount,'year':payment_year}).render_qweb_pdf([line.partner_id.id], data={})[0]
                        file = base64.encodestring(pdf)
                        vals = {
                            'partner_id': line.partner_id.id,
                            'amount': line.amount,
                            'file':file,
                            'file_name':line.partner_id.name +"_1099 Form.pdf"
                        }
                        vendor_data.append((0, 0, vals))
                        exist_vendor.append(line.partner_id.id)
            self.vendor_ids = vendor_data

        view_id = self.env.ref('us_1099_form.view_1099_mail_wizard').id
        return {
            'name': _('1099 Form'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acc.mail.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
             }

    @api.multi
    def send_1099_mail(self):
        if self.vendor_ids:
            try:
                template_id = self.env.ref('us_1099_form.template_send_1099')
            except ValueError:
                template_id = False
            form_ids = []
            count = 0
            for vendor in self.vendor_ids:
                if vendor.select:
                    template_id.write({'email_to': vendor.partner_id.email})
                    template_id.with_context({'amount':vendor.amount}).send_mail(vendor.partner_id.id, force_send=True)
                    vendor_data = {
                        'partner_id':vendor.partner_id.id,
                        'amount':vendor.amount,
                        'file':vendor.file,
                        'file_name':vendor.file_name,
                    }
                    form_id = self.env["sent.1099.forms"].create(vendor_data).id
                    form_ids.append((form_id))
                    count +=1
                if count == 0:
                    raise UserError(_('Please select at least one vendor to send mail!'))
        else:
            raise UserError(_('Please add some Vendors to send mail!'))

        view_id = self.env.ref('us_1099_form.view_sent_1099_tree').id
        return {
            'name': _('Sent 1099 Forms'),
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', form_ids)],
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sent.1099.forms',
            'view_id': view_id,
        }