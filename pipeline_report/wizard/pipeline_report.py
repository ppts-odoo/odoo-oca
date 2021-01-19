from odoo import api, fields, models, _
from datetime import datetime
import base64
import unicodedata
import xlwt
from odoo.tools import html2plaintext
import platform
from odoo.http import request
from urllib.parse import urljoin

class AccountMailWizard(models.TransientModel):
    _name = "pipeline.report.wizard"

    user_ids = fields.Many2many("res.users", string="Sales Person")
    xl_file = fields.Binary(" Download File")
    xl_name = fields.Char("File name")
    select_all = fields.Boolean("Select all")
    crm_stage_ids = fields.Many2many('crm.stage', string='Stages', default=lambda self: self.env['crm.stage'].search([]))

    @api.onchange('select_all')
    def onchange_select_all(self):
        if self.select_all:
            self.user_ids = False

    def generate_xl_report(self):
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour("custom_colour", 0x20)
        xlwt.add_palette_colour("custom_colour0", 0x21)
        xlwt.add_palette_colour("custom_colour1", 0x22)
        xlwt.add_palette_colour("custom_colour2", 0x16)
        xlwt.add_palette_colour("custom_colour3", 0x09)
        workbook.set_colour_RGB(0x20, 0, 49, 53)
        workbook.set_colour_RGB(0x21, 242, 242, 242)
        workbook.set_colour_RGB(0x22, 113, 178, 226)
        workbook.set_colour_RGB(0x16, 233, 238, 242)
        workbook.set_colour_RGB(0x09, 255, 255, 255)
        if self.select_all:
            user_ids = self.env['res.users'].search([('is_salesperson', '=', True)])
        else:
            user_ids = self.user_ids
        for user in user_ids:
            sheet = workbook.add_sheet(user.name, cell_overwrite_ok=True)
            sheet.show_grid = False
            sheet.col(1).width = 256 * 40
            sheet.col(2).width = 256 * 15
            sheet.col(3).width = 256 * 17
            sheet.col(4).width = 256 * 15
            sheet.col(5).width = 256 * 50

            style0 = xlwt.easyxf('font: name Century Gothic, height 300,bold True;align: horiz center;pattern:pattern solid,fore-colour custom_colour0;', num_format_str='YYYY-MM-DD')
            style00 = xlwt.easyxf('font: name Century Gothic, colour white, bold True;pattern:pattern solid,fore-colour custom_colour1;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,'
                                  'left thin,right thin,top thin,bottom thin;align: vert top;', num_format_str='#,##0.00')
            style01 = xlwt.easyxf('font: name Century Gothic, colour white, bold True;pattern:pattern solid,fore-colour custom_colour;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,'
                                  'left thin,right thin,top thin,bottom thin;align: vert top;',num_format_str='"$"#,##0.00')
            style02 = xlwt.easyxf('font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour3;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;', num_format_str='"$"#,##0.00')
            style03 = xlwt.easyxf('font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour2;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;', num_format_str='"$"#,##0.00')

            sheet.write_merge(2, 3, 1, 7, 'PROJECT REPORT ' + '(' + str(datetime.today().date()) + ')', style0)
            sheet.write(5, 1, 'SALES REP', style00)
            sheet.write(5, 2, str(user.name).upper(), style00)
            sheet.write(5, 3, '', style00)
            sheet.write(5, 4, '', style00)
            sheet.write(5, 5, '', style00)
            n = 5;
            for stage in self.crm_stage_ids:
                n += 1
                leads = self.env['crm.lead'].search([('user_id', '=', user.id), ('stage_id', '=', stage.id)])
                sheet.write(n, 1, str(stage.name).upper() + ' [ Projects # ' + format(len(leads)) + ' ]', style01)
                sheet.write(n, 2, 'VALUE', style01)
                sheet.write(n, 3, 'REVENUE', style01)
                sheet.write(n, 4, 'CLOSING DATE', style01)
                sheet.write(n, 5, 'NOTES', style01,)
                n += 2;

                i = 0;planned_revenue = 0
                for lead in leads:
                    last_msg = ''
                    message = lead.message_ids.filtered(lambda s: s.message_type == 'comment')
                    if message and html2plaintext(message[0].body):
                        last_msg = html2plaintext(message[0].body)

                    if i == 0:
                        new_style = style02
                        i = 1
                    else:
                        new_style = style03
                        i = 0
                    sheet.write(n - 1, 1, lead.name or '', new_style)
                    sheet.write(n - 1, 2, lead.expected_revenue, new_style)
#                     sheet.write(n - 1, 3, lead.sale_amount_total, new_style)
                    sheet.write(n - 1, 3, lead.date_deadline or '', new_style)
                    sheet.write(n - 1, 4, last_msg or '', new_style)
                    planned_revenue += lead.expected_revenue
#                     sale_amount_total += lead.sale_amount_total
                    n += 1
                sheet.write(n-1, 1, 'TOTAL', style01)
                sheet.write(n-1, 2, planned_revenue, style01)
#                 sheet.write(n-1, 3, sale_amount_total, style01)
                
        if platform.system() == 'Linux':
                filename = ('/tmp/Pipeline Report-' + str(datetime.today().date()) + '.xls')
        else:
           filename = ('Pipeline Report-' + str(datetime.today().date()) + '.xls')
        # filename = ('Pipeline Report - ' + str(datetime.today().date()) + '.xls')
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        attach_vals = {
            'xl_file' :out,
            'xl_name':filename.split('/')[2],
            'select_all': self.select_all,
            'user_ids': [(6, False, [x.id for x in self.user_ids])],
            'crm_stage_ids': [(6, False, [x.id for x in self.crm_stage_ids])],
        }

        act_id = self.env['pipeline.report.wizard'].create(attach_vals)
        fp.close()
       
        return {
            'name': _('Pipeline Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pipeline.report.wizard',
            'target': 'new',
            'res_id':act_id.id,
            }

    def preview_report(self):
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
        page_url = urljoin(base_url, "pipeline_report/pipeline_report_web_view/")

        request.session['stage_ids'] = self.crm_stage_ids.ids

        if self.select_all:
            user_ids = self.env['res.users'].search([('is_salesperson', '=', True)])
        else:
            user_ids = self.user_ids

        request.session['user_list'] = user_ids.ids

        return {
            'type': 'ir.actions.act_url',
            'name': "Pipeline Web Report",
            'target': '_blank',
            'url': page_url
        }