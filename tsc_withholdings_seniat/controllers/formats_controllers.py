# -*- coding: utf-8 -*-
# from odoo import http


# class TscFormatsForSeniat(http.Controller):
#     @http.route('/tsc_formats_for__seniat/tsc_formats_for__seniat', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tsc_formats_for__seniat/tsc_formats_for__seniat/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tsc_formats_for__seniat.listing', {
#             'root': '/tsc_formats_for__seniat/tsc_formats_for__seniat',
#             'objects': http.request.env['tsc_formats_for__seniat.tsc_formats_for__seniat'].search([]),
#         })

#     @http.route('/tsc_formats_for__seniat/tsc_formats_for__seniat/objects/<model("tsc_formats_for__seniat.tsc_formats_for__seniat"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tsc_formats_for__seniat.object', {
#             'object': obj
#         })

