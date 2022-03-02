# -*- coding: utf-8 -*-
from odoo import http

# class FiscalYearSequenceExtensible(http.Controller):
#     @http.route('/fiscal_year_sequence_extensible/fiscal_year_sequence_extensible/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fiscal_year_sequence_extensible/fiscal_year_sequence_extensible/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fiscal_year_sequence_extensible.listing', {
#             'root': '/fiscal_year_sequence_extensible/fiscal_year_sequence_extensible',
#             'objects': http.request.env['fiscal_year_sequence_extensible.fiscal_year_sequence_extensible'].search([]),
#         })

#     @http.route('/fiscal_year_sequence_extensible/fiscal_year_sequence_extensible/objects/<model("fiscal_year_sequence_extensible.fiscal_year_sequence_extensible"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fiscal_year_sequence_extensible.object', {
#             'object': obj
#         })