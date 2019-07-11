from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row


class WebsiteSale(WebsiteSale):
      
    @http.route(['/shop/get_products_list'], type='json', auth='public', website=True)
    def get_products_list(self, search_value=None, search_category=None):
        values = ''
        products = request.env['product.template'].search([('website_published', '=',  True), ('name', 'ilike', search_value)])
        website_categories = []
        if search_value!='' and products:
            if search_category == 'all':
                for product in products:
                    if product.public_categ_ids:
                        for category in product.public_categ_ids:
                            if category.id not in website_categories:  
                                # append product category to category list                  
                                website_categories.append(category.id)
                                values += "<div><a href='/shop/search_string/"+str(search_value)+"/"+str(category.id)+"'>"+str(search_value)+"<span> in </span><b>"+str(category.name)+"</b></a><br/></div>"
            else:
                products = request.env['product.template'].search([('website_published', '=',  True), ('name', 'ilike', search_value), ('public_categ_ids', 'in', [search_category])])
                if products:
                    category = request.env['product.public.category'].search([('id', '=', search_category)])
                    values += "<div><a href='/shop/search_string/"+str(search_value)+"/"+str(category.id)+"'>"+str(search_value)+"<span> in </span><b>"+str(category.name)+"</b></a><br/></div>"
            
                
        return values

    @http.route(['/shop/search_string/<string:search>/<model("product.public.category"):website_category>'], type='http', auth='public', website=True)
    def search_string(self, search, website_category, category='',ppg=PPG, page=0, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        if website_category != '':
            category = website_category
            
            
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, vals.split("-")) for vals in attrib_list if vals]
        attributes_ids = set([vals[0] for vals in attrib_values])
        attrib_set = set([vals[1] for vals in attrib_values])
        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
        pricelist_context = dict(request.env.context)
        #price details of product categories 
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if category:
            post["website_category"] = category.id
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False)])
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            # compare and append current category with parent category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
        all_categs = request.env['product.public.category'].search([])

        ProductAttribute = request.env['product.attribute']
        if products:
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        # category list with all details of products
        compute_currency = lambda price: from_currency.compute(price, to_currency)
        values = {
            'search': '',
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'all_categories':all_categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }
        
        return request.render("website_sale.products", values)
    
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='',website_category='', ppg=False,**post):
        if website_category == 'all':
            category = None
        if website_category != '' and website_category != 'all':
            category = website_category
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, vals.split("-")) for vals in attrib_list if vals]
        attributes_ids = set([vals[0] for vals in attrib_values])
        attrib_set = set([vals[1] for vals in attrib_values])

        domain = self._get_search_domain(search, category, attrib_values)
        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))
        pricelist_context = dict(request.env.context)
        # product pricelist
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if category:
            category = request.env['product.public.category'].browse(int(category))
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False)])
        all_categs = request.env['product.public.category'].search([])
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        product_count = Product.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)
        # searchbox products information
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'all_categories':all_categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)
    
    
