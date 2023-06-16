# -*- coding: utf-8 -*-
from odoo import http

# class JplProductivity(http.Controller):
#     @http.route('/jpl_productivity2_2/jpl_productivity2_2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jpl_productivity2_2/jpl_productivity2_2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jpl_productivity2_2.listing', {
#             'root': '/jpl_productivity2_2/jpl_productivity2_2',
#             'objects': http.request.env['jpl_productivity2_2.jpl_productivity2_2'].search([]),
#         })

#     @http.route('/jpl_productivity2_2/jpl_productivity2_2/objects/<model("jpl_productivity2_2.jpl_productivity2_2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jpl_productivity2_2.object', {
#             'object': obj
#         })