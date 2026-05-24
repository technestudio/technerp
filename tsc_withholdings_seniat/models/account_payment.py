# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    temp_sequence_withholding_iva = fields.Char(
        string="Temporary IVA withholding sequence",
        copy=False,
        readonly=True,
    )
    temp_sequence_withholding_islr = fields.Char(
        string="Temporary ISLR withholding sequence",
        copy=False,
        readonly=True,
    )

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        payments = self._create_payments()

        if self.group_payment == False:
            for line in self.line_ids:
                move = line.move_id
                if move.withholding_iva != 0.0 and not move.sequence_withholding_iva:
                    move.generate_withholding_iva()
                if move.withholding_islr != 0.0 and not move.sequence_withholding_islr:
                    move.generate_withholding_islr()
        else:
            sequence_iva = False
            sequence_islr = False

            for line in self.line_ids:
                move = line.move_id
                if move.withholding_iva != 0.0 and not move.sequence_withholding_iva:
                    sequence_iva = self.env['ir.sequence'].next_by_code('account.move.withholding.iva')
                if move.withholding_islr != 0.0 and not move.sequence_withholding_islr:
                    sequence_islr = self.env['ir.sequence'].next_by_code('account.move.withholding.islr')
                break

            for line in self.line_ids:
                move = line.move_id
                if move.withholding_iva != 0.0 and not move.sequence_withholding_iva and sequence_iva:
                    move.validation_generation_withholding("withholding_iva", "sequence_withholding_iva")
                    move.sequence_withholding_iva = sequence_iva
                if move.withholding_islr != 0.0 and not move.sequence_withholding_islr and sequence_islr:
                    move.validation_generation_withholding("withholding_islr", "sequence_withholding_islr")
                    move.sequence_withholding_islr = sequence_islr

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })

        return action
    