from odoo import models, fields,api,_
from urllib.parse import urljoin
from odoo.addons.website.models.website import slugify
from odoo.exceptions import UserError
import xlwt
import base64
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self,vals):
        if vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id','=',vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).create(vals)

#     @api.multi
    def write(self, vals):
        if vals.get('partner_id') or vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id', '=', vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).write(vals)

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    
    print_url = fields.Char("Print link", compute="_compute_url")

    def _compute_url(self):
        """ Computes a public URL for the purchase comparison """
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
        for record in self:
            record.print_url = urljoin(base_url, "purchase_comparison_chart/purchase_comparison/%s" % (slugify(record)))
    
#     @api.multi
    def show_terms_condition(self, value1, value2):
        if value1 and value2:
            va = str(value1).strip()
            terms_condition = self.env['purchase.order'].search([('requisition_id', '=',self.id), ('partner_id', '=', int(va))])
            if terms_condition:
                return terms_condition.notes
            else:
                return None
        
#     @api.multi
    def purchase_comparison(self):
        """ Open the website page with the purchase comparison form """
        self.ensure_one()
        if self.order_count == 0:
            raise UserError(_('No RFQ available for the Purchase agreement. Please add some RFQ to compare'))
        return {
            'type': 'ir.actions.act_url',
            'name': "Purchase Comparison Chart",
            'target': 'self',
            'url': self.with_context(relative_url=True).print_url
        }

#     @api.multi
    def print_xl(self):
        purchase_orders = self.env['purchase.order'].search([('requisition_id', '=', self.id)])
        for rec in purchase_orders:
            for line in rec.order_line:
                price_unit = line.price_unit
                price_subtotal = line.price_subtotal
                     
            style2 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
            style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz right;', num_format_str='#,##0.00')
            style1 = xlwt.easyxf('font: name Times New Roman, bold on,height 250; pattern: pattern solid, fore_colour black;', num_format_str='#,##0.00')
        
            workbook = xlwt.Workbook()

            sheet = workbook.add_sheet(self.name)
            sheet.write_merge(2, 2, 4, 6, 'PURCHASE  COMPARISON', style1)
            sheet.write(3, 7,'PRC No', style0)
            sheet.write(3, 8, self.name, style0)
            sheet.write(4, 7, 'Date',style0)
            sheet.write(4, 8, self.ordering_date,style0)
                      
            sheet.write_merge(6, 6, 0, 1, 'PRODUCT DETAILS', style1)
            sheet.write(8, 3, 'S NO',style1)
            sheet.write_merge(8, 8, 4, 5, 'MATERIAL',style1)
            sheet.write_merge(8, 8, 6, 7, 'UOM',style1)
            sheet.write(8, 8, 'QTY',style1)

            n = 9; i = 1
            for line in self.line_ids:
                sheet.write(n, 3, i, style2)
                sheet.write_merge(n, n,4,5, line.product_id.name, style0)
                sheet.write_merge(n, n,6,7, line.product_uom_id.name, style0)
                sheet.write(n,8, line.product_qty, style0)
                n +=1; i += 1

            ams_time = datetime.now()
            date = ams_time.strftime('%m-%d-%Y %H.%M.%S')
            filename = ('Report' + '-' + date + '.xls')
            workbook.save(filename)

            fp = open(filename, "rb")
            file_data = fp.read()
            attach_id = self.env['report.wizard'].create({'attachment': base64.encodestring(file_data),
                                                          'attach_name': 'Report.xls'})
            fp.close()

        return {
            'type': 'ir.actions.act_window',
            'name': ('Report'),
            'res_model': 'report.wizard',
            'res_id': attach_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }


class PaymentWizard(models.TransientModel):
    _name = 'report.wizard'
    _description = 'Report Details'

    attachment = fields.Binary('Excel Report File', nodrop=True, readonly=True)
    attach_name = fields.Char('Attachment Name')







