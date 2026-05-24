# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class tsc_formats_for__seniat(models.Model):
#     _name = 'tsc_formats_for__seniat.tsc_formats_for__seniat'
#     _description = 'tsc_formats_for__seniat.tsc_formats_for__seniat'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

