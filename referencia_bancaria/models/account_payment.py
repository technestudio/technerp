# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class accountPayme(models.Model):
    _inherit = "account.payment"

    referencia = fields.Char(string='Nro. Referencia')  
    is_bank_selected = fields.Boolean(string="is bank selected", default=False)

    _sql_constraints = [
        ('referencia_unique', 'unique(referencia)', 'Nro. de Referencia ya existe!')
    ]

    @api.onchange('journal_id','is_internal_transfer')
    def _change_journal_id(self):
        
        if self.journal_id.type == 'bank' and self.is_internal_transfer == False:
            self.is_bank_selected = True
        else:     
            self.is_bank_selected = False 
            self.referencia = ''

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)

        if payments['referencia'] == False and payments['journal_id'].type == 'bank' and payments['is_internal_transfer'] == False:
            self.referencia = ''
            raise ValidationError('El Campo Nro. de Referencia no puede estar Vacio')
        else:
            return payments
        