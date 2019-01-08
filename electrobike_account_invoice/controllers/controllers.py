# -*- coding: utf-8 -*-
from odoo import http

# class /home/suriel/projects/electrobike/electrobikeAccountInvoice(http.Controller):
#     @http.route('//home/suriel/projects/electrobike/electrobike_account_invoice//home/suriel/projects/electrobike/electrobike_account_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/suriel/projects/electrobike/electrobike_account_invoice//home/suriel/projects/electrobike/electrobike_account_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/suriel/projects/electrobike/electrobike_account_invoice.listing', {
#             'root': '//home/suriel/projects/electrobike/electrobike_account_invoice//home/suriel/projects/electrobike/electrobike_account_invoice',
#             'objects': http.request.env['/home/suriel/projects/electrobike/electrobike_account_invoice./home/suriel/projects/electrobike/electrobike_account_invoice'].search([]),
#         })

#     @http.route('//home/suriel/projects/electrobike/electrobike_account_invoice//home/suriel/projects/electrobike/electrobike_account_invoice/objects/<model("/home/suriel/projects/electrobike/electrobike_account_invoice./home/suriel/projects/electrobike/electrobike_account_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/suriel/projects/electrobike/electrobike_account_invoice.object', {
#             'object': obj
#         })