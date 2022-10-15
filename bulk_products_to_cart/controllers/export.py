# -*- coding: utf-8 -*-
from odoo import http
from openpyxl import Workbook
from odoo import api, fields, models, _
from odoo.http import request
from odoo.osv import expression
import xlwt,base64
from xlrd import open_workbook
from io import BytesIO
from odoo.http import content_disposition, request
from odoo.tools.misc import xlsxwriter
from odoo.addons.website.controllers.main import QueryURL
import io


class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey, ppr):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= ppr:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(ppr):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=20, ppr=4):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(p.website_size_x, 1), ppr)
            y = min(max(p.website_size_y, 1), ppr)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % ppr, pos // ppr, x, y, ppr):
                pos += 1
            # if 21st products (index 20) and the last line is full (ppr products in it), break
            # (pos + 1.0) / ppr is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // ppr) > maxy:
                break

            if x == 1 and y == 1:  # simple heuristic for CPU optimization
                minpos = pos // ppr

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // ppr) + y2][(pos % ppr) + x2] = False
            self.table[pos // ppr][pos % ppr] = {
                'product': p, 'x': x, 'y': y,
                'ribbon': p.website_ribbon_id,
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // ppr))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows

class WebsiteSale(http.Controller):

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    def _get_pricelist_context(self):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        return pricelist_context, pricelist

    def _get_search_order(self, post):

        order = post.get('order') or 'website_sequence ASC'
        return 'is_published desc, %s, id desc' % order

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        request.session['export_products'] = values.get('products').ids
        request.session['product_price'] = values.get('pricelist').id
        return request.render("website_sale.products", values)


    @http.route('/shop/export', type='http', auth='public')
    def export(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 14, 'font_color': 'black'})
        format = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'font_color': '#753B6F'})
        sheet = workbook.add_worksheet('Export')
        sheet.set_column("A:A", 10)
        sheet.set_column("B:B", 10)
        sheet.set_column("C:C", 10)
        sheet.set_column("D:D", 10)
        sheet.set_column("E:E", 10)
        sheet.write(0, 0, 'Product Name', style)
        sheet.write(0, 1, 'Description', style)
        sheet.write(0, 2, 'Price', style)
        sheet.write(0, 3, 'Quantity to Order', style)
        sheet.write(0, 4, 'Product ID', style)


        products = request.session['export_products']
        product_variant = request.env['product.product'].sudo().search([('product_tmpl_id','in',products)])
        pricelist = request.session['product_price']
        pricelist = request.env['product.pricelist'].sudo().browse(pricelist)
        i = 1
        for variant in product_variant:
            product_pricelist = variant.product_tmpl_id._get_combination_info(product_id=variant.id, pricelist=pricelist)
            sheet.write(i, 0, variant.product_tmpl_id.name, format),
            sheet.write(i, 1, variant.name, format),
            sheet.write(i, 2, str(product_pricelist.get('price')) + " " + str(pricelist.currency_id.symbol), format),
            sheet.write(i, 3, "0", format),
            sheet.write(i, 4, variant.id, format)
            i = i + 1

        workbook.close()
        xlsx_data = output.getvalue()
        filename='Export'
        response = request.make_response(xlsx_data,
                                         headers=[('Content-Type',
                                                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                                  ('Content-Disposition', content_disposition(filename + '.xlsx'))],
                                         )
        return response

    @http.route('/shop/add_to_cart', type='http', auth='public', method=['GET','POST'], csrf=False, website=True)
    def excel_add_to_cart(self,**post):

        attachment = post.get("myfile")
        excel_file = attachment.read()
        wb = open_workbook(file_contents=excel_file)
        sheet_name = wb.sheet_names()
        worksheet = wb.sheet_by_name(sheet_name[0])
        first_row = []
        try:
            for col in range(0, worksheet.ncols):
                first_row.append(worksheet.cell_value(0,col).strip())

            datas = []
            for row in range(1,worksheet.nrows):
                elm = {}
                for col in range(0, len(first_row)):
                    elm[first_row[col]] = worksheet.cell_value(row, col)
                datas.append(elm)
            order = request.website.sale_get_order(force_create=True)

            for data in datas:
                if int(data.get('Quantity to Order')) > 0:
                    product_id = request.env['product.product'].sudo().browse(int(data.get('Product ID')))
                    get_line = order.order_line.filtered(lambda l: l.product_id.id==product_id.id)
                    if get_line:
                        get_line[0].product_uom_qty = get_line[0].product_uom_qty+int(data.get('Quantity to Order'))
                    else:
                        order._cart_update(
                            product_id=int(product_id.id),
                            add_qty=int(data.get('Quantity to Order')),
                            set_qty=0,
                        )



        except Exception as e:
            pass

        return request.redirect("/shop/cart")







