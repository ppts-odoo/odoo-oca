# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _

class WebsiteCustom(http.Controller):
    
    @http.route("/help_desk/form", type='http', auth="user", website=True, csrf=False)
    def help_desk_main_form(self,*args, **kw):
        
        company_id = request.env['res.company'].sudo().search([])
        master_id = request.env['master.menu'].sudo().search([])
        sub_master_id = request.env['sub.menu'].sudo().search([])
        values = {
                'companies':company_id,
                'masters':master_id,
                'sub_masters':sub_master_id,
                }
        
        return request.render("helpdesk_website.create_help_desk_form",values)
    
    @http.route("/body_contents/<int:pages_ids>", type='http',method="post", auth="user", website=True, csrf=False)
    def body_contents(self, pages_ids, **post):
        
        pages_id = request.env['page.content'].sudo().search([('sub_menu_id','=',pages_ids)])
        pages_main_id = request.env['page.content'].sudo().search([('sub_menu_id','=',pages_ids)],limit=1)

        values = {
                'pages':pages_id,
                'page_main':pages_main_id,
                }
        return request.render("helpdesk_website.create_help_desk_form_pages",values)
    
    