# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class accountPaymeRegister(models.TransientModel):
    _inherit = "account.payment.register"

    referencia = fields.Char(string="Nro. Referencia", copy=False, help="Ingrese el Nro. de Referencia del Banco")  
    is_bank_selected = fields.Boolean(string="is bank selected", default=False)

    _sql_constraints = [
        ('referencia_unique', 'unique(referencia)', 'Nro. de Referencia ya existe!')
    ]

    @api.onchange('journal_id')
    def _change_journal_id(self):
        if self.journal_id.type == 'bank':
            self.is_bank_selected = True
        else:     
            self.is_bank_selected = False 
            self.referencia = ''

    def _create_payment_vals_from_wizard(self):
        if self.referencia == False and self.journal_id.type == 'bank':
            self.referencia = ''
            raise ValidationError('El Campo Nro. de Referencia no puede estar Vacio')
        else:
            payment_vals = super()._create_payment_vals_from_wizard()
            payment_vals['referencia'] = self.referencia
            return payment_vals

    def _create_payment_vals_from_batch(self):
        if self.referencia == False and self.journal_id.type == 'bank':
            self.referencia = ''
            raise ValidationError('El Campo Nro. de Referencia no puede estar Vacio')
        else:
            batch_values = super()._create_payment_vals_from_batch()
            batch_values['referencia'] = self.referencia
            return batch_values

