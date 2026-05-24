# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    def _post_payments(self, to_process, edit_mode=False):
        super(TscAccountPaymentRegister, self)._post_payments(to_process, edit_mode)
        
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']

        for tsc_payment in payments:
            tsc_actual_move = self.env["account.move"].browse(self.env.context.get("active_id"))
            if (
                tsc_payment.journal_id.tsc_generate_ITF 
                and tsc_payment.journal_id.type == "bank"
                and tsc_actual_move.move_type == "in_invoice"
            ):
                tsc_payment.tsc_create_itf_move()  
                tsc_payment.tsc_itf_move_id._post(soft=False)

        


