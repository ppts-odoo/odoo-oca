# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

class ValidateBid(http.Controller):
    @http.route(['/purchase_comparison_chart/purchase_comparison/<model("purchase.requisition"):purchase_requisition_id>'], type='http', auth='public', website=True)
    def purchase_comparison(self, purchase_requisition_id, **post):
        supplier_ids = []; product_ids=[]; values = []; amt = []; number = []; supplier_id = []
        counts = 1
        for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id)]):
            # Append supplier
            supplier_ids.append({'supplier_id':record.partner_id.id, 'sname':record.partner_id.name})
            supplier_id.append(record.partner_id.id)
            number.append(counts)
            # Append Products and quantity
            counts +=1
            for line in record.order_line:
                if values:
                    if line.product_id.id not in product_ids:
                        product_ids.append(line.product_id.id)
                        values.append({'product_id':line.product_id.id, 'product_name':line.product_id.name, 'price':line.price_unit, 'uom':line.product_id.uom_po_id.name, 'qty':line.product_qty})
                else:
                    product_ids.append(line.product_id.id)
                    values.append({'product_id':line.product_id.id,'product_name':line.product_id.name, 'price':line.price_unit, 'uom':line.product_id.uom_po_id.name,'qty':line.product_qty})
        
        count = 0; supplier_amount_total = []; no_of_col = 2 ; even_number = [] ; odd_number = []
        # Append amount based on the products and supplier
        for separate_values in values:
            for suppliers in supplier_ids:
                for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id),('partner_id', '=',suppliers['supplier_id'])]):
                    for po_line in request.env['purchase.order.line'].search([('order_id', '=', record.id),('product_id', '=',separate_values['product_id'])]):
                        amt.append({'total_amount':(po_line.product_qty * po_line.price_unit), 'price':po_line.price_unit})
            values[count]['amt'] = amt
            count +=1
            amt = []
        # Generate number to create rows and columns
        total_supplier = len(number)
        if total_supplier >= 2:
            increase_by_supplier = total_supplier * no_of_col
        else:
            increase_by_supplier = no_of_col
        if total_supplier > 1:
            total_no = range(1, increase_by_supplier + 1)
            supplier_amount_total_1 = list(range(1, increase_by_supplier + 1))
        else:
            total_no = range(1, increase_by_supplier)
            supplier_amount_total_1 = list(range(1, increase_by_supplier))
        for c_number in total_no:
            if c_number%2 ==0:
                even_number.append(c_number)
            else:
                odd_number.append(c_number)
        for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id)]):
            supplier_amount_total.append(record.amount_total)
        # Update the amount in even number position
        tcount = 1    
        for i in even_number:        
            supplier_amount_total_1[i-1] = supplier_amount_total[tcount-1]
            tcount +=1
        # Update the supplier id in odd number position
        scount = 1
        for odd_no in odd_number:
            for total in total_no:
                if total == odd_no:                  
                    supplier_amount_total_1[odd_no-1] = supplier_id[scount-1]
                    scount +=1
        return request.render('purchase_comparison_chart.purchase_comparison', {'data':values, 'supplier':supplier_ids,'purchase_requisition_id':purchase_requisition_id, 
                                                               'number':number, 'to_no':total_no, 'column_no':even_number, 'supplier_amount_total':supplier_amount_total,
                                                                'supplier_amount_total_1':supplier_amount_total_1, 'odd_number':odd_number})