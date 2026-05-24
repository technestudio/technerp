# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountPayment(models.Model):

    _inherit = 'account.payment'

    def tsc_get_itf_for_igtf_amount(self):
        tsc_amount_conversion = self.tsc_igtf_payment_journal.currency_id._convert(
            self.tsc_igtf_payment_amount_journal_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        return (
            tsc_amount_conversion 
            * self.tsc_igtf_payment_journal.tsc_itf_percentage
        ) / 100

    def tsc_get_itf_for_igtf_original_amount(self):
        return (
            self.tsc_igtf_payment_amount_journal_currency 
            * self.tsc_igtf_payment_journal.tsc_itf_percentage
        ) / 100

    def tsc_record_itf_for_igtf_lines(self):
        self.ensure_one()
        tsc_itf_amount = self.tsc_get_itf_for_igtf_amount()
        tsc_itf_original_amount = self.tsc_get_itf_for_igtf_original_amount()

        tsc_shared_values = {
            'name': _('ITF of IGTF of ') + self.tsc_return_liquidity_name(),
            'date_maturity': self.date,
            'partner_id': self.company_id.id,
            'currency_id': self.tsc_igtf_payment_journal.currency_id.id or self.currency_id.id,
        }
        
        tsc_line_vals_list = [
            # Débito.
            {
                **tsc_shared_values,
                'amount_currency': tsc_itf_original_amount,
                'debit': tsc_itf_amount,
                'credit': 0.0,
                'account_id': self.tsc_igtf_payment_journal.tsc_ITF_account_expense.id,
            },
            # Crédito.
            {
                **tsc_shared_values,                        
                'amount_currency': -tsc_itf_original_amount,
                'debit': 0.0,
                'credit': tsc_itf_amount,
                'account_id': self.tsc_igtf_payment_journal.default_account_id.id,
            },
        ]   

        return tsc_line_vals_list

    def write(self, vals):    
        res = super().write(vals)

        if "tsc_igtf_move_id" in vals:
            for record in self:
                if (
                    record.partner_type == 'supplier' 
                    and record.tsc_igtf_payment_journal.tsc_generate_ITF
                    and record.tsc_igtf_move_id.id
                ):
                    tsc_line_vals_list = self.tsc_record_itf_for_igtf_lines()
                    tsc_new_account_move = self.env['account.move'].create({
                        'journal_id': self.tsc_igtf_payment_journal.id,
                        'line_ids': [(0, 0, line_vals) for line_vals in tsc_line_vals_list],
                        'payment_id': self.id,
                        'move_type': 'entry',
                        'ref': self.ref or "",
                    })
                    tsc_new_account_move._post(soft=False)
                    record.tsc_igtf_move_id.write({'tsc_itf_move_id': tsc_new_account_move.id})
            
        return res



                
                