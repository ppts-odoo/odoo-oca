# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import re
from odoo.exceptions import UserError

class BulkAddToCart(http.Controller):
    
    @http.route(['/bulk_products',], auth="public", website=True, csrf=False)
    def add_bulk_to_cart(self, msg=None, **kw):
        total_alt_product = 0
        if kw.get('total_alt_products', '') == '':
            total_alt_product = 0
        else:
            total_alt_product = int(kw.get('total_alt_products', 0)) + 1
        alt_ids = []; alt_list_ids = []; alt_values = {}
        for i in range(0, total_alt_product):
            if kw.get('alt_id_' + str(i)) and kw.get('alt_qty_' + str(i)):
                alt_ids.append(int(kw.get('alt_id_' + str(i))))
                alt_list_ids.append({'product_id':int(kw.get('alt_id_' + str(i))), 'qty':int(kw.get('alt_qty_' + str(i)))})
                alt_values.update({'alt_qty_' + str(i):int(kw.get('alt_qty_' + str(i)))})
        total_org_product = 0
        if kw.get('total_org_products', '') == '':
            total_org_product = 0
        else:
            total_org_product = int(kw.get('total_org_products', 0)) + 1
        org_ids = []; org_list_ids = []; org_values = {}
        for i in range(0, total_org_product):
            org_qty = 0
            if kw.get('org_id_' + str(i)):
                org_ids.append(int(kw.get('org_id_' + str(i))))
                if kw.get('org_qty_' + str(i)) == '':
                    org_qty = 0
                else:
                    org_qty = int(kw.get('org_qty_' + str(i)))
                org_list_ids.append({'product_id':int(kw.get('org_id_' + str(i))), 'qty':org_qty})
                org_values.update({'org_qty_' + str(i):org_qty})
        org_qty = 0
        try:
            description = str(kw.get('description'))
            description = description.replace('\t', '').replace('\r', '').strip()
            content = description.splitlines()
            chunks = [content[x:x + 1] for x in range(0, len(content), 1)]
            new_list = [];update_list = []
            for item in chunks:
                lst2 = []
                item = ','.join(map(str, item)) 
                values = item.split(',')
                if len(values) == 3:
                    reference = values[0]
                    qty = values[1]
                    comment = values[2]
                    if str(qty).isdigit() == True:
                        lst2.extend((reference, qty, comment))
                        update_list.append(lst2)
                    else:
                        product_qty_msg = '<div class="alert alert-danger"><strong>Warning ! </strong> Please check product quantity.Only integers are accepted.</div>'
                        return request.render("add_to_cart_quick.add_bulk_products_form", {"product_qty":product_qty_msg}) 
                elif len(values) == 2:
                    reference = values[0]
                    qty = values[1]
                    comment = '-'
                    if str(qty).isdigit() == True:
                        lst2.extend((reference, qty, comment))
                        update_list.append(lst2)
                    else:
                        product_qty_msg = '<div class="alert alert-danger"><strong>Warning ! </strong> Please check product quantity.Only integers are accepted.</div>'
                        return request.render("add_to_cart_quick.add_bulk_products_form", {"product_qty":product_qty_msg}) 
                elif len(values) >= 4:
                    reference = values[0]
                    qty = values[1]
                    desc = values[2:]
                    comment = ",".join(desc)
                    if str(qty).isdigit() == True:
                        lst2.extend((reference, qty, comment))
                        update_list.append(lst2)
                    else:
                        product_qty_msg = '<div class="alert alert-danger"><strong>Warning ! </strong> Please check product quantity.Only integers are accepted.</div>'
                        return request.render("add_to_cart_quick.add_bulk_products_form", {"product_qty":product_qty_msg})
                elif len(values) == 1:
                    if values[0] == 'None':
                       return request.render("add_to_cart_quick.add_bulk_products_form")
                    else:
                        reference = values[0]
                        qty = 1
                        comment = '-'
                        lst2.extend((reference, qty, comment))
                        update_list.append(lst2) 
            new_list.append(update_list)
            search = str(kw.get('search'))
            create_order = str(kw.get('create_order'))
            if search == 'Search' and not description:
                msg = '<div class="alert alert-danger"><strong>Warning ! </strong> Please import order with the given format.</div>'
                return request.render("add_to_cart_quick.add_bulk_products_form", {"msg":msg}) 
            else:
                msg = None
            if search == 'Update the order' or search == 'Search':
                results = []; total_amounts = discounts = 0.00;
                warehouse_ids = request.env['stock.warehouse'].sudo().search([])
                for list in new_list:
                    for item in list:
                        default_code = str(item[0])
                        product_id = request.env['product.product'].sudo().search(['|', ('default_code', '=', default_code.lower()), ('default_code', '=', default_code.upper())], limit=1)
                        if not product_id:
                            product_id = request.env['product.product'].sudo().search([('name', '=', str(item[0]))], limit=1)
                        if not product_id:
                            product_id = request.env['product.product'].sudo().search([('default_code', 'ilike', str(item[0]))], limit=1)
                        flag = False;
                        alernative_ids = []
                        if product_id:
                            original_id = product_id
                            if product_id:
                                for record in results:
                                    total_amount = 0.00; amount = 0.00
                                    if record['products'] != None:
                                        if product_id.id == record['products']:
                                            total_amount =round(request.website.pricelist_id.currency_id.round(int(item[1]) * product_id.list_price),2)
                                            total_amounts +=total_amount
                                            record['qty'] += int(item[1])
                                            record['comment'] = record['comment'] + ',' + (str(item[2]))
                                            record['total'] += float(total_amount)
                                            break
                                        else:
                                            discount = 0
                                            if original_id.id == product_id.id:
                                                org_qty = 0
                                                org = False
                                                if product_id.id in org_ids:
                                                    for p in org_list_ids:
                                                        if product_id.id == p.get('product_id', 0):
                                                            org = True
                                                            org_qty =int(p.get('qty', 0))
                                                if org:
                                                    total_amount =round(request.website.pricelist_id.currency_id.round(org_qty * product_id.list_price), 2)
                                                    total_amounts += total_amount
                                                else:
                                                    org_qty=int(item[1])
                                                    total_amount =round(request.website.pricelist_id.currency_id.round(org_qty * product_id.list_price), 2)
                                                    total_amounts += total_amount
                                                
                                            else:
                                                if product_id.id in alt_ids:
                                                    for p in alt_list_ids:
                                                        if product_id.id == p.get('product_id', 0):
                                                            total_amount =round(request.website.pricelist_id.currency_id.round(int(p.get('qty', 0)) * product_id.list_price), 2)
                                                            total_amounts += total_amount
                                            if original_id.id != product_id.id:
                                                results.append({'products':product_id.id, 'internal_ref':product_id.default_code, 'qty': int(item[1]),
                                                            'ask_ref':'Alternative of '+str(item[0])+' reference.','comment':str(item[2]), 'product_name':product_id.name, 'qty_available':product_id.sudo().qty_available, 'lst_price':round(product_id.lst_price, 2),
                                                            'discount':discount, 'final_price':round(product_id.list_price, 2),'alt':True,
                                                            'total':total_amount})
                                            else:
                                                results.append({'products':product_id.id, 'internal_ref':product_id.default_code,'qty': int(item[1]),
                                                            'ask_ref':str(item[0]),'comment':str(item[2]), 'product_name':product_id.name, 'qty_available':product_id.sudo().qty_available, 'lst_price':round(product_id.lst_price, 2),
                                                            'discount':discount, 'final_price':round(product_id.list_price, 2),'alt':False,
                                                            'total':total_amount})
                                            break
                                if not results:
                                    total_amount = 0.00
                                    if original_id.id == product_id.id:
                                        org_qty = 0.00
                                        org = False
                                        if product_id.id in org_ids:
                                            for p in org_list_ids:
                                                if product_id.id == p.get('product_id', 0):
                                                    org = True
                                                    org_qty =int(p.get('qty', 0))
                                        if org:
                                            total_amount =round(request.website.pricelist_id.currency_id.round(org_qty * product_id.list_price), 2)
                                            total_amounts += total_amount
                                        else:
                                            total_amount =round(request.website.pricelist_id.currency_id.round(int(item[1]) * product_id.list_price),2)
                                            total_amounts += total_amount
                                    discount = 0.00; final_price =0.00
                                    if original_id.id != product_id.id:
                                        final_price = ("%.2f" % product_id.list_price) or ("%.2f" % product_id.lst_price)
                                        results.append({'products':product_id.id, 'internal_ref':product_id.default_code, 'qty': int(item[1]), 'comment':str(item[2]),
                                                        'ask_ref':'Alternative of '+str(item[0])+' reference.','product_name':product_id.name, 'qty_available':product_id.sudo().qty_available, 'lst_price':("%.2f" % product_id.lst_price),
                                                        'discount':discount, 'final_price':float(final_price), 'total':total_amount,'alt':True})
                                    else:
                                        final_price = ("%.2f" % product_id.list_price) or ("%.2f" % product_id.lst_price)
                                        results.append({'products':product_id.id, 'internal_ref':product_id.default_code,'qty': int(item[1]), 'comment':str(item[2]),
                                                        'ask_ref':str(item[0]),'product_name':product_id.name, 'qty_available':product_id.sudo().qty_available, 'lst_price':round(product_id.lst_price, 2),
                                                        'discount':discount, 'final_price':float(final_price), 'total':total_amount,'alt':False,})
                        else:
                            results.append({'products':None, 'internal_ref':'Not Available','qty': int(item[1]),
                                            'ask_ref':str(item[0]),'comment':str(item[2]), 'product_name':'Not Available', 'qty_available':'-',
                                            'lst_price':'-', 'total':'-', 'list_price':'-','alt':False,
                                            'discount':'-', 'final_price':'-', 'total':'-'})
                            flag = True
                if discounts:
                    amt = total_amounts
                    total_amt = ("%.2f" % (amt))
                    return_values = {
                        'description': description,
                        'results': results,
                        'alt_values':alt_values,
                        'org_values':org_values,
                        'total_amounts':float(total_amt)
                    }
                else:
                    return_values = {
                        'description': description,
                        'results': results,
                        'alt_values':alt_values,
                        'org_values':org_values,
                        'total_amounts':float("%.2f" % total_amounts),
                    }
                if search == 'Update the order' or search == 'Search':
                    return request.render("add_to_cart_quick.add_bulk_products_form", return_values)
            else:
                for cart in new_list:
                    for record in cart:
                        product_id = request.env['product.product'].sudo().search(['|', ('default_code', '=', str(record[0]).lower()), ('default_code', '=', str(record[0]).upper())], limit=1)
                        if not product_id:
                            product_id = request.env['product.product'].sudo().search([('name', '=', str(record[0])), ], limit=1)
                        if not product_id:
                            product_id = request.env['product.product'].sudo().search([('default_code', 'ilike', str(item[0]))], limit=1)
                        if product_id:
                            org_qty = 0
                            org = False
                            if product_id.id in org_ids:
                                for p in org_list_ids:
                                    if product_id.id == p.get('product_id', 0):
                                        org = True
                                        org_qty =int(p.get('qty', 0))
                            if org and org_qty > 0:
                                order = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id.id), add_qty=float(org_qty), set_qty=0,display=False)
                for cart in alt_list_ids:
                    order = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(cart.get('product_id')), add_qty=float(cart.get('qty')), set_qty=0,display=False)
                            
                sale_order_id = request.session.get('sale_order_id')
                if sale_order_id:
                    sale_order_id = request.env['sale.order'].with_context(force_company=request.website.company_id.id).sudo().browse(sale_order_id).exists() if sale_order_id else None
                return request.redirect('/shop/cart')
        except Exception as e:
            raise UserError(e)
