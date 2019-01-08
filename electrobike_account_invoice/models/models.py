# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class /home/suriel/projects/electrobike/electrobike_account_invoice(models.Model):
#     _name = '/home/suriel/projects/electrobike/electrobike_account_invoice./home/suriel/projects/electrobike/electrobike_account_invoice'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100