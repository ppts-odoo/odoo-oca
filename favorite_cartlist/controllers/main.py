# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import models
import werkzeug


class FavoritesCart(http.Controller):

# // Main menu
    @http.route('/favorites/', auth="user", website=True, csrf=False)
    def favorites(self, **kw):
        values = {}
           
        favroites = request.env['website.favorites'].sudo().search([('user_id', '=', request.env.uid)])

        values.update({
            'favorites': favroites,
            })
        
        return http.request.render("favorite_cartlist.favorites_cart", values)
 
    @http.route(['/favorites/<int:favorites>'], auth="user", website=True)
    def favorite_products(self, favorites, **kw):
        
        values = {}
        
        favorites_list = request.env['favorites.list'].sudo().search([('favorite_id', '=', favorites)])
        
        values.update({
            'favorites_list': favorites_list,
            })
        
        return http.request.render("favorite_cartlist.favorite_list", values)    


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart'], type='http', auth="user", website=True)
    def cart(self, **post):
        order = request.website.sale_get_order()
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        if post.get('code_not_available'):
            values['code_not_available'] = post.get('code_not_available')

        favorites = request.env['website.favorites'].sudo().search([])
 
        values.update({
            'favorites': favorites,
            })

        return request.render("website_sale.cart", values)
 
    @http.route('/favorite_message/', auth="user", website=True, csrf=False)
    def favorite_message(self, **kw):
        values = {}
        return http.request.render("favorite_cartlist.favorite_message", values)
    
    @http.route(['/check_favorites'], type='http', auth="public", website=True, csrf=False)
    def check_favorites(self, **post):
        
        sale_id = request.env['sale.order'].sudo().search([('id', '=', int(post.get('y')))])
        if sale_id.order_line:
            existing_favorite_id = request.env['website.favorites'].sudo().search([('name', '=', post.get('x')), ('user_id', '=', request.env.uid)])
            
            if existing_favorite_id:
                return 'True'
            else:
                return 'False'
        else:
            return 'Null'
    
    @http.route(['/create_favorites'], type='http', auth="user", website=True, csrf=False)
    def create_favorites(self, **post):
        products_list = []
        sale_id = request.env['sale.order'].sudo().search([('id', '=', post.get('sale_order'))])
        if sale_id.order_line:
            existing_favorite_id = request.env['website.favorites'].sudo().search([('name', '=', post.get('favorite_name')), ('user_id', '=', request.env.uid)])
            if not existing_favorite_id:
                for products in sale_id.order_line:
                    products_list.append({'product':products.product_id.id, 'qty':products.product_uom_qty})
                
                if post.get('favorites') == "create_new_fav":
                    favorite = request.env['website.favorites'].create({
                                                            'name': post.get('favorite_name'),
                                                            })
                    for line in products_list:
                        favorite.write({'favorites_ids':[(0, 0, {'product_id':line['product'], 'product_qty':line['qty']})]})
                 
                else:
                    favorite_id = request.env['website.favorites'].sudo().search([('id', '=', post.get('favorites'))])
                    
                    for loop in products_list:
                        favorites_ids = {'favorites_ids':[(0, 0, {'product_id':loop['product'], 'product_qty':loop['qty']})]}
                        
                        favorite_id.write(favorites_ids)
                return request.redirect('/favorites')
        
    @http.route(['/delete_favorites'], type='http', auth="user", website=True, csrf=False)
    def delete_favorites(self, **post):
        if post:
            delete_ids = post.get('boxes')
            product = int(delete_ids.split("_")[1])
            
            favorite_id = int((delete_ids.split("_")[2]))
            
            product_id = request.env['favorites.list'].sudo().search([('product_id', '=', product), ('favorite_id', '=', favorite_id)])

            product_id.unlink()
            
            return "True"
            
    @http.route(['/delete_favorites_list'], type='http', auth="user", website=True, csrf=False)
    def delete_favorites_list(self, **post):
        if post:
            delete_ids = post.get('boxes')
            
            favorite = int(delete_ids.split("_")[2])
            
            favorite_id = request.env['website.favorites'].sudo().search([('id', '=', favorite)])

            favorite_id.unlink()
            
            return "True"

    @http.route(['/add_to_cart_favorites'], type='http', auth="user", website=True, csrf=False)
    def add_to_cart_favorites(self, **post):
        
        favorite_id = request.env['website.favorites'].sudo().search([('id', '=', post.get('favorite_id'))])
        if not post.get('sale_order_id'):
            sale_id = request.website.sale_get_order(force_create=1)
            
            sale_id.partner_id = request.env.user.partner_id.id
            sale_id.partner_invoice_id = request.env.user.partner_id.id
            sale_id.partner_shipping_id = request.env.user.partner_id.id
            
            for loop in favorite_id.favorites_ids:
                order_line = {'order_line':[(0, 0, {'product_id': loop.product_id.id,
                                           'product_uom_qty': loop.product_qty,
                                           'price_unit': loop.product_id.lst_price,
                                           'name': loop.product_id.name,
                                           })]}
                sale_id.write(order_line)        
        else:
            sale_id = request.env['sale.order'].sudo().search([('id', '=', post.get('sale_order_id'))])
    
            for loop in favorite_id.favorites_ids:
                order_line = {'order_line':[(0, 0, {'product_id': loop.product_id.id,
                                           'product_uom_qty': loop.product_qty,
                                           'price_unit': loop.product_id.lst_price,
                                           'name': loop.product_id.name,
                                           })]}
                sale_id.write(order_line)        
        
        return "True"

    @http.route('/remove', auth="user", website=True, csrf=False)
    def favorites(self, **kw):
        
        msg = '<div class="alert alert-success"><strong>Success ! </strong> The favorite(s) has been deleted successfully.</div>'
    
        return http.request.render("favorite_cartlist.deleted_form", {"msg":msg})


class Website(models.Model):
    _inherit = "website"

    def count_favorites(self):

        favorite_id = request.env['website.favorites'].sudo().search_count([('user_id', '=', request.env.uid)])

        return int(favorite_id)
    
