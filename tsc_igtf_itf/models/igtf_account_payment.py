# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountPayment(models.Model):

    _inherit = 'account.payment'

    tsc_currency_id_apply_IGTF = fields.Boolean(string="Does the currency apply IGTF?", 
                                                related="currency_id.tsc_apply_IGTF") 
    
    tsc_with_igtf = fields.Boolean(string="Include IGTF",
                                    help="Include in the IGTF payment. An associated accounting entry will be generated.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=False,
                                    tracking=True,
                                    default=False)

    tsc_igtf_payment_journal = fields.Many2one(string="IGTF Registration Journal",
                                    comodel_name="account.journal",
                                    help="Accounting journal in which the IGTF payment will be recorded.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=False,
                                    tracking=True,
                                    default=False,
                                    domain="[('tsc_is_igtf_journal','=',True)]")

    tsc_igtf_payment_journal_currency = fields.Many2one(string="IGTF Registration Journal Currency",
                                                       related="tsc_igtf_payment_journal.currency_id")

    tsc_igtf_payment_amount = fields.Monetary(string="IGTF amount",
                                    help="IGTF Payment Amount.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    tracking=False,
                                    default=0.00,
                                    compute="tsc_compute_igtf_payment_amount",
                                    currency_field='currency_id')

    tsc_igtf_payment_amount_journal_currency = fields.Monetary(string="IGTF amount in IGTF's Currency",
                                    help="IGTF Payment Amount in IGTF Journal Currency.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    tracking=False,
                                    default=0.00,
                                    compute="tsc_compute_igtf_payment_amount_journal_currency",
                                    currency_field='tsc_igtf_payment_journal_currency')

    tsc_amount_with_igtf = fields.Monetary(string="Total payment",
                                    help="Total payment to receive including IGTF.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    tracking=False,
                                    default=0.00,
                                    compute="tsc_compute_amount_with_igtf",
                                    currency_field='currency_id')

    tsc_amount_with_igtf_journal_currency = fields.Monetary(string="Total payment in IGTF's Currency",
                                    help="Total payment to receive including IGTF in IGTF Journal Currency.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    tracking=False,
                                    default=0.00,
                                    compute="tsc_compute_igtf_payment_amount_journal_currency",
                                    currency_field='tsc_igtf_payment_journal_currency')    

    tsc_show_igtf_currency = fields.Boolean(string="Show IGTF amounts in the journal currency?",
                                           compute="tsc_compute_show_igtf_currency")

    tsc_igtf_move_id = fields.Many2one(comodel_name='account.move',
                                       string='IGTF Journal Entry',
                                       required=False, 
                                       store=True,
                                       readonly=True,
                                       check_company=True,
                                       copy=False)


    @api.onchange('partner_id', 'tsc_igtf_payment_amount')
    def tsc_onchange_partner_amount(self):
        for record in self:
            if record.tsc_igtf_move_id.id:
                tsc_moves = self.env['account.move'].browse(record.tsc_igtf_move_id.id)
                if tsc_moves.exists():
                    tsc_liquidity_line_name = ''.join(
                        x[1] for x in self._get_liquidity_aml_display_name_list()
                    )
                    tsc_amount_conversion = self.currency_id._convert(
                        record.tsc_igtf_payment_amount,
                        self.company_id.currency_id,
                        self.company_id,
                        self.date,
                    )
                    for line in tsc_moves.line_ids:
                        tsc_line = self.env['account.move.line'].browse(line.id)
                        tsc_line.partner_id = record.partner_id.id
                        tsc_line.name = _('IGTF of ') + tsc_liquidity_line_name


    def tsc_record_igtf_lines(self):
        tsc_liquidity_line_name = (
            ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        )

        # helping fields
        tsc_igtf_currency = self.tsc_igtf_payment_journal_currency
        tsc_company_currency = self.company_id.currency_id
        tsc_sum = (
            self.tsc_igtf_payment_amount_journal_currency 
            if self.tsc_show_igtf_currency 
            else self.tsc_igtf_payment_amount
        )
        tsc_sum_currency = tsc_igtf_currency if self.tsc_show_igtf_currency else self.currency_id
                
        tsc_amount_conversion = tsc_sum_currency._convert(
            tsc_sum,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )

        tsc_shared_values = {
            'name': _('IGTF of ') + tsc_liquidity_line_name,
            'date_maturity': self.date,
            'currency_id': tsc_sum_currency.id,
            'partner_id': self.partner_id.id,
        }
        
        def tsc_read_method(tsc_field, tsc_account_type):
            tsc_line_with_method = (
                self.tsc_igtf_payment_journal[tsc_field].filtered(
                    lambda line: (
                        line.payment_method_id.id == self.payment_method_line_id.payment_method_id.id
                    )
                )
            )
            if tsc_line_with_method.payment_account_id.id:
                return tsc_line_with_method.payment_account_id.id
            else:
                tsc_account_settings = self.company_id[
                    f'account_journal_payment_{tsc_account_type}_account_id'
                ]
                if tsc_account_settings.id:
                    return tsc_account_settings.id
            return self.tsc_igtf_payment_journal.default_account_id.id

        tsc_payment_method = self.tsc_igtf_payment_journal.default_account_id.id
        if self.payment_type == "inbound" and self.partner_type == 'customer':
            tsc_payment_method = tsc_read_method("inbound_payment_method_line_ids", "debit")
        elif self.payment_type == "outbound" and self.partner_type == 'supplier':
            tsc_payment_method = tsc_read_method("outbound_payment_method_line_ids", "credit")
            
        line_vals_list = [
            # Debit.
            {
                **tsc_shared_values,
                'amount_currency': tsc_sum,
                'debit': tsc_amount_conversion,
                'credit': 0.0,
                'account_id': (
                    tsc_payment_method
                    if self.partner_type == 'customer'
                    else self.tsc_igtf_payment_journal.tsc_igtf_expense.id
                ),
            },
            # Credit.
            {
                **tsc_shared_values,                        
                'amount_currency': -tsc_sum,
                'debit': 0.0,
                'credit': tsc_amount_conversion,
                'account_id': (
                    self.tsc_igtf_payment_journal.tsc_igtf_account.id
                    if self.partner_type == 'customer'
                    else tsc_payment_method
                ),
            },
        ]   

        return line_vals_list

    @api.onchange("amount")
    def tsc_onchange_amount(self):
        for record in self:
            if record.tsc_igtf_move_id.id:
                raise UserError(_('In order to change the payment amount, please reverse the IGTF-related movement.'))

    @api.onchange("partner_id")
    def tsc_onchange_partner_id(self):
        for record in self:
            tsc_move = record.tsc_igtf_move_id
            if tsc_move.id:
                for line in tsc_move.line_ids:
                    tsc_liquidity_line_name = ''.join(
                        x[1] for x in self._get_liquidity_aml_display_name_list()
                    )
                    line.write({
                        'partner_id': record.partner_id.id,
                        'name': _('IGTF of ') + tsc_liquidity_line_name,
                    })

    @api.depends('amount', 'tsc_igtf_payment_journal')
    def tsc_compute_igtf_payment_amount(self):
        for record in self:
            tsc_multiplication = (
                record.amount * record.tsc_igtf_payment_journal.tsc_igtf_percentage
            )
            record.tsc_igtf_payment_amount = tsc_multiplication / 100

    @api.depends('tsc_igtf_payment_journal_currency', 'currency_id')
    def tsc_compute_show_igtf_currency(self):
        for record in self:
            record.tsc_show_igtf_currency = (
                record.tsc_igtf_payment_journal_currency.id 
                and record.tsc_igtf_payment_journal_currency.id != record.currency_id.id
            )

    @api.depends(
        'currency_id', 
        'tsc_igtf_payment_amount', 
        'tsc_amount_with_igtf', 
        'tsc_igtf_payment_journal_currency'
    )
    def tsc_compute_igtf_payment_amount_journal_currency(self):
        for record in self:
            # igtf's origin journal currency
            tsc_igtf_currency = record.tsc_igtf_payment_journal_currency
            # if igtf currency is available, use it. if not, use the company's currency.
            tsc_currency_id = (
                tsc_igtf_currency 
                if tsc_igtf_currency.name 
                else record.company_id.currency_id
            )
            # currency conversion
            record.tsc_igtf_payment_amount_journal_currency = record.currency_id._convert(
                record.tsc_igtf_payment_amount,
                tsc_currency_id,
                record.company_id,
                record.date,
            )
            record.tsc_amount_with_igtf_journal_currency = record.currency_id._convert(
                record.tsc_amount_with_igtf,
                tsc_currency_id,
                record.company_id,
                record.date,
            )

    @api.depends('amount', 'tsc_igtf_payment_amount')
    def tsc_compute_amount_with_igtf(self):
        for record in self:
            record.tsc_amount_with_igtf = record.amount + record.tsc_igtf_payment_amount

    def tsc_button_igtf_journal(self):
        self.ensure_one()
        return {
            'name': _("IGTF Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.tsc_igtf_move_id.id,
        }


    def tsc_create_igtf_move(self):
        if self.tsc_igtf_payment_journal:
            line_vals_list = self.tsc_record_igtf_lines()
            tsc_new_account_move = self.env['account.move'].browse(self.move_id._origin.id).copy({
                'journal_id': self.tsc_igtf_payment_journal.id,
                'line_ids': [(0, 0, line_vals) for line_vals in line_vals_list],
                'payment_id': self.id,
            })
            self.write({'tsc_igtf_move_id': tsc_new_account_move.id})
            self.tsc_igtf_move_id._post(soft=False)
        else:
            raise UserError(_("An IGTF journal is needed to complete this action."))

    
    @api.onchange('tsc_igtf_payment_journal')
    def tsc_onchange_igtf_move_id(self):
        for record in self:
            if record.tsc_igtf_move_id.posted_before:
                raise UserError(_('You cannot edit the journal of an account move if it has been posted once.'))

    def tsc_check_invoice_moves(self):
        tsc_keys = ["reconciled_bill_ids", "reconciled_invoice_ids"]
        for record in self:
            for tsc_key in tsc_keys:
                for invoice in record[tsc_key]:
                    invoice.tsc_compute_igtf_amounts()

    def write(self, vals):    
        res = super().write(vals)
        
        for record in self:
            if record.tsc_with_igtf and not record.tsc_igtf_move_id.id:
                record.tsc_create_igtf_move() 

        if "tsc_with_igtf" in vals:
            self.tsc_check_invoice_moves()
            
        return res

    def tsc_activate_igtf(self):
        self.tsc_with_igtf = True
            
    def tsc_clean_igtf_fields(self):
        self.tsc_with_igtf = False
        self.tsc_igtf_move_id = False
        self.tsc_igtf_payment_amount = 0.0
        self.tsc_igtf_payment_journal = False
            
    def tsc_deactivate_igtf(self):
        if self.tsc_igtf_move_id.id:
            tsc_reversal_move = self.env['account.move.reversal'].create({
                'move_ids': [(6, 0, [self.tsc_igtf_move_id.id])],
                'journal_id': self.tsc_igtf_payment_journal.id,
            })
            return tsc_reversal_move.reverse_moves()            

    
    def action_cancel(self):
        ''' draft -> cancelled '''
        super().action_cancel()
        return self.tsc_deactivate_igtf()

    def action_draft(self):
        ''' posted -> draft '''
        super().action_draft()
        return self.tsc_deactivate_igtf()
        