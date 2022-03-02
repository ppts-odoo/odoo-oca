# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import xlwt
import base64
from io import StringIO
from odoo import api, fields, models, _
import platform

class PurchaseReportOut(models.Model):        
    _name = 'purchase.report.out'
    _description = 'purchase order report'
    
    purchase_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Purchase Excel Report', readonly=True)
    purchase_work = fields.Char('Name', size=256)
    file_names = fields.Binary('Purchase CSV Report', readonly=True)
    
   
class WizardWizards(models.Model):        
    _name = 'wizard.reports'
    _description = 'purchase wizard'
    
#purchase order excel report button actions               
    @api.multi
    def action_purchase_report(self):          
#XLS report         
        custom_value = {}
        label_lists=['PO','POR','CLIENTREF','BARCODE','DEFAULTCODE','NAME','QTY','VENDORPRODUCTCODE','TITLE', 'PARTNERNAME', 'EMAIL', 'PHONE', 'MOBILE', 'STREET', 'STREET2', 'ZIP', 'CITY', 'COUNTRY']                    
        order = self.env['purchase.order'].browse(self._context.get('active_ids', list()))      
        workbook = xlwt.Workbook()                      
        for rec in order:              
            purchase = []                                                          
            for line in rec.order_line:                              
                product = {}                                                                       
                product ['product_id'] = line.product_id.name                                                                            
                product ['product_qty'] = line.product_qty                            
                product ['qty_received'] = line.qty_received                           
                product ['qty_invoiced'] = line.qty_invoiced                                              
                product ['price_unit'] = line.price_unit                        
                product ['taxes_id'] = line.taxes_id.name                      
                product ['price_subtotal'] = str(line.price_subtotal)+' '+line.currency_id.symbol                        
                purchase.append(product)
                                                                                           
            custom_value['products'] = purchase               
            custom_value ['partner_id'] = rec.partner_id.name
            custom_value ['partner_ref'] = rec.partner_ref
            custom_value ['payment_term_id'] = rec.payment_term_id.name
            custom_value ['date_order'] = rec.date_order
            custom_value ['partner_no'] = rec.name
            custom_value ['amount_total'] = str(rec.amount_total)+' '+rec.currency_id.symbol
            custom_value ['amount_untaxed'] = str(rec.amount_untaxed)+' '+rec.currency_id.symbol
            custom_value ['amount_tax'] = str(rec.amount_tax)+' '+rec.currency_id.symbol
                                                  
            style0 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz right;', num_format_str='#,##0.00')
            style1 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;', num_format_str='#,##0.00')
            style2 = xlwt.easyxf('font:height 400,bold True;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
            style3 = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
            style4 = xlwt.easyxf('font:bold True;  borders:top double,right thin;align: horiz right;', num_format_str='#,##0.00')
            style5 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;', num_format_str='#,##0')
            style6 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
            style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
            style8 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz right;', num_format_str='DD-MM-YYYY')
            style3_1 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin;align: horiz right;', num_format_str='#,##0.00')
            style4_1 = xlwt.easyxf('borders:top thin;', num_format_str='#,##0.00')
            style5_1 = xlwt.easyxf('borders:left thin;', num_format_str='#,##0.00')
            style6_1 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
            style7_1 = xlwt.easyxf('borders:left thin,bottom thin,right thin;', num_format_str='#,##0.00')
            style8_1 = xlwt.easyxf('borders:right thin;', num_format_str='#,##0.00')
            sheet = workbook.add_sheet(rec.name)
            
            sheet.write_merge(2, 3, 3, 6, 'Purchase   Order :', style2)
            sheet.write_merge(2, 3, 7, 8, custom_value['partner_no'], style2)     
            sheet.write(5, 1, 'Vendor', style3)
            sheet.write(6, 1, '',style3_1)
            sheet.write(7, 1, '',style3_1)
            sheet.write(8, 1, '',style3_1)
            sheet.write(9, 1, '',style3_1)
            sheet.write(5, 3, '',style4_1)
            sheet.write(5, 4, '',style4_1)
            sheet.write(5, 5, '',style4_1)
            sheet.write(5, 6, '',style4_1)
            sheet.write(5, 7, '',style4_1)
            sheet.write(8, 12,'', style5_1)
            sheet.write(9, 12,'', style5_1)
            sheet.write(5, 2, custom_value['partner_id'], style0)     
            sheet.write_merge(5, 5, 8, 9, 'Order  Date', style3)
            sheet.write_merge(5, 5, 10, 11, custom_value['date_order'], style8)     
            sheet.write_merge(6, 6, 8, 9, 'Vendor Reference', style3)
            sheet.write_merge(6, 6, 10, 11, custom_value['partner_ref'], style0)
            sheet.write_merge(7, 7, 8, 9, 'Payment Terms', style3)
            sheet.write_merge(7, 7, 10, 11, custom_value['payment_term_id'], style0)

            sheet.write(10, 1, 'S NO', style1)                           
            sheet.write_merge(10, 10, 2, 3, 'PRODUCT', style1)
            sheet.write_merge(10, 10, 4, 5, 'QUANTITY', style1)        
            sheet.write_merge(10, 10, 6, 7, 'UNIT PRICE', style1)
            sheet.write_merge(10, 10, 8, 10, 'TAXES', style1) 
            sheet.write(10, 11, 'SUBTOTAL', style1)
            
            n = 11; m=10; i = 1
            for product in custom_value['products']:
                sheet.write(n, 1, i, style5)  
                sheet.write_merge(n, n, 2, 3, product['product_id'], style6)      
                sheet.write_merge(n, n, 4, 5, product['product_qty'], style0)
                sheet.write_merge(n, n, 6, 7, product['price_unit'], style0)
                sheet.write_merge(n, n, 8, 10, product['taxes_id'], style0)
                sheet.write(n, 11, product['price_subtotal'], style0)                          
                n += 1; m +=1; i += 1
            sheet.write_merge(n+1, n+1, 9, 10, 'Untaxed Amount', style7)
            sheet.write(n+1, 11, custom_value['amount_untaxed'], style4)
            sheet.write_merge(n+2, n+2, 9, 10, 'Taxes', style7)
            sheet.write(n+2, 11, custom_value['amount_tax'], style4)
            sheet.write_merge(n+3, n+3, 9, 10, 'Total', style6_1)
            sheet.write(n+3, 11, custom_value['amount_total'], style4)
            sheet.write(m+1, 1, '', style3_1)
            sheet.write(m+1, 11, '', style8_1)
            sheet.write(n+1, 1, '', style3_1)
            sheet.write(n+2, 1, '', style3_1)
            sheet.write(n+3, 1, '', style3_1)
            sheet.write_merge(n+4,n+4,1, 11, '', style7_1)
#CSV report
        datas = []
        for values in order:
            for value in values.order_line:
                if value.product_id.seller_ids:
                    item = [
                            str(value.order_id.name or ''),
                            str(''),
                            str(''),                            
                            str(value.product_id.barcode or ''),
                            str(value.product_id.default_code or ''),
                            str(value.product_id.name or ''),
                            str(value.product_qty or ''),
                            str(value.product_id.seller_ids[0].product_code or ''),
                            str(value.partner_id.title or ''),
                            str(value.partner_id.name or ''),
                            str(value.partner_id.email or ''),
                            str(value.partner_id.phone or ''),
                            str(value.partner_id.mobile or ''),
                            str(value.partner_id.street or ''),
                            str(value.partner_id.street2 or ''),
                            str(value.partner_id.zip or ''),
                            str(value.partner_id.city or ''),
                            str(value.partner_id.country_id.name or ' '),                        
                            ] 
                    datas.append(item)    
            
        output = StringIO()
        label = ';'.join(label_lists)               
        output.write(label)         
        output.write("\n")
                     
        for data in datas:       
            record = ';'.join(data)
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(),"utf-8"))


        if platform.system() == 'Linux':
            filename = ('/tmp/Purchase Report' + '.xls')
        else:
            filename = ('Purchase Report' + '.xls')

        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
                       
# Files actions         
        attach_vals = {
                'purchase_data': 'Purchase Report'+ '.xls',
                'file_name': out,
                'purchase_work':'Purchase'+ '.csv',
                'file_names':data,
            } 
            
        act_id = self.env['purchase.report.out'].create(attach_vals)
        fp.close()
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.report.out',
        'res_id': act_id.id,
        'view_type': 'form',
        'view_mode': 'form',
        'context': self.env.context,
        'target': 'new',
        }
                          
        

 





























