# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountPayment(models.Model):

    _inherit = 'account.payment'

    tsc_itf_move_id = fields.Many2one(comodel_name='account.move',
                                       string='ITF Journal Entry',
                                       required=False, 
                                       store=True,
                                       readonly=True,
                                       check_company=True,
                                       copy=False)

    def tsc_create_itf_move(self):
        self.ensure_one()

        line_vals_list = self.tsc_record_itf_lines()

        tsc_new_account_move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, line_vals) for line_vals in line_vals_list],
            'payment_id': self.id,
            'move_type': 'entry',
            'ref': self.ref or "",
        })
        self.write({'tsc_itf_move_id': tsc_new_account_move.id})

    def tsc_return_liquidity_name(self):
        return ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())

    def tsc_record_itf_lines(self):

        self.ensure_one()
        # lines' tag/description
        tsc_liquidity_line_name = self.tsc_return_liquidity_name()

        # lines' amount      
        tsc_itf_amount = self.tsc_get_itf_amount()
        tsc_itf_original_amount = self.tsc_get_itf_original_amount()

        tsc_shared_values = {
            'name': _('ITF of ') + tsc_liquidity_line_name,
            'date_maturity': self.date,
            'currency_id': self.currency_id.id,
            'partner_id': self.company_id.id,
        }
        
        line_vals_list = [
            # Debit.
            {
                **tsc_shared_values,
                'amount_currency': tsc_itf_original_amount,
                'debit': tsc_itf_amount,
                'credit': 0.0,
                'account_id': self.journal_id.tsc_ITF_account_expense.id,
            },
            # Credit.
            {
                **tsc_shared_values,                        
                'amount_currency': -tsc_itf_original_amount,
                'debit': 0.0,
                'credit': tsc_itf_amount,
                'account_id': self.journal_id.default_account_id.id,
            },
        ]   

        return line_vals_list

    def tsc_is_itf_bank_journal(self):
        return (self.journal_id.type == "bank" 
                and self.journal_id.tsc_generate_ITF)

    def tsc_outbound_payment_condition(self):
        return (self.partner_type in ("customer", "supplier") 
                and self.payment_type == "outbound" and not self.is_internal_transfer)
    
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if (
                record.tsc_is_itf_bank_journal() 
                and not self.tsc_itf_move_id.id 
                and record.tsc_outbound_payment_condition()
               ):
                record.tsc_create_itf_move()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "amount" in vals:
            for record in self:
                tsc_move = record.tsc_itf_move_id
                if tsc_move.id != False:
                    tsc_move.line_ids.unlink()
                    line_vals_list = record.tsc_record_itf_lines()
                    tsc_move.write({
                        'line_ids': [(0, 0, line_vals) for line_vals in line_vals_list],
                    })
                    
        if "journal_id" in vals or "payment_type" in vals:
            for record in self:
                if (
                    record.tsc_is_itf_bank_journal() 
                    and not self.tsc_itf_move_id.id 
                    and record.tsc_outbound_payment_condition()
                ):
                    record.tsc_create_itf_move()   
                
                if (
                    record.tsc_itf_move_id.id
                    and (
                        not record.tsc_is_itf_bank_journal()
                        or not record.tsc_outbound_payment_condition()
                        )
                ):
                    record.tsc_itf_move_id.button_cancel()
                    
        return res

    def tsc_deactivate_itf(self):
        if self.tsc_itf_move_id.id:
            tsc_reversal_move = self.env['account.move.reversal'].create({
                'move_ids': [(6, 0, [self.tsc_itf_move_id.id])],
                'journal_id': self.journal_id.id,
            })
            return tsc_reversal_move.reverse_moves()         

    def action_post(self):
        ''' draft -> posted '''
        super().action_post()
        if self.tsc_itf_move_id.state not in ('cancel', 'posted'):
            self.tsc_itf_move_id._post(soft=False)

    def action_draft(self):
        ''' posted -> draft '''
        super().action_draft()
        if self.tsc_itf_move_id.state and self.tsc_itf_move_id.state not in ('draft'):
            self.tsc_itf_move_id.button_draft()

    def action_cancel(self):
        ''' draft -> cancelled '''
        super().action_cancel()
        if self.tsc_itf_move_id.state and self.tsc_itf_move_id.state not in ('cancel', 'posted'):
            self.tsc_itf_move_id.button_cancel()
    
    @api.onchange("partner_id")
    def tsc_onchange_partner_id(self):
        for record in self:
            tsc_move = record.tsc_itf_move_id
            if tsc_move.id != False:
                for line in tsc_move.line_ids:
                    tsc_liquidity_line_name = self.tsc_return_liquidity_name()
                    line.write({
                        'name': _('ITF of ') + tsc_liquidity_line_name,
                    })

    def tsc_get_itf_original_amount(self):
        return (
            self.amount 
            * self.journal_id.tsc_itf_percentage
        ) / 100
    
    def tsc_get_itf_amount(self):
        tsc_amount_conversion = self.currency_id._convert(
            self.amount,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        return (
            tsc_amount_conversion 
            * self.journal_id.tsc_itf_percentage
        ) / 100

    def tsc_button_itf_journal(self):
        self.ensure_one()
        return {
            'name': _("ITF Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.tsc_itf_move_id.id,
        }
                