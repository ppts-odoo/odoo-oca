# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import models
import werkzeug
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request

_logger = logging.getLogger(__name__)


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

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get(
                    'sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get(
                    'sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

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
        
        sale_id = request.env['sale.order'].sudo().search([('id', '=', (post.get('y')))])
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
    
