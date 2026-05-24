# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    tsc_currency_id_apply_IGTF = fields.Boolean(string="Does the currency apply IGTF?", 
                                                default=False) 

    tsc_with_igtf = fields.Boolean(string="Include IGTF",
                                    help="Include in the IGTF payment. An associated accounting entry will be generated.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=False,
                                    default=False)

    tsc_igtf_payment_journal = fields.Many2one(string="IGTF Registration Journal",
                                    comodel_name="account.journal",
                                    help="Accounting journal in which the IGTF payment will be recorded.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=False,
                                    default=False,
                                    domain="[('tsc_is_igtf_journal','=',True)]")

    tsc_igtf_payment_amount = fields.Monetary(string="IGTF amount",
                                    help="IGTF Payment Amount.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    default=0.00,
                                    compute="tsc_compute_igtf_payment_amount",
                                    currency_field='currency_id')

    tsc_amount_with_igtf = fields.Monetary(string="Total payment",
                                    help="Total payment to receive including IGTF.",
                                    required=True,
                                    readonly=True,
                                    store=True,
                                    copy=False,
                                    default=0.00,
                                    compute="tsc_compute_amount_with_igtf",
                                    currency_field='currency_id')
    

    @api.onchange('currency_id')
    def tsc_compute_currency_id_apply_IGTF(self):
        context_getter = lambda key: self._context.get(key, False)
        for record in self:
            record.tsc_currency_id_apply_IGTF = False
            if (tsc_id := context_getter("active_id")) and context_getter("active_model") == "account.move.line":
                tsc_allowed_move = self.env["account.move"].browse(tsc_id).move_type
                if tsc_allowed_move in ("out_invoice", "in_invoice"):
                    record.tsc_currency_id_apply_IGTF = record.currency_id.tsc_apply_IGTF

    @api.depends('amount', 'tsc_igtf_payment_journal')
    def tsc_compute_igtf_payment_amount(self):
        for record in self:
            record.tsc_igtf_payment_amount = 0.00
            tsc_multiplication = record.amount * record.tsc_igtf_payment_journal.tsc_igtf_percentage
            if tsc_multiplication != 0:
                record.tsc_igtf_payment_amount = tsc_multiplication / 100

    @api.depends('amount', 'tsc_igtf_payment_amount', 'tsc_currency_id_apply_IGTF')
    def tsc_compute_amount_with_igtf(self):
        for record in self:
            record.tsc_amount_with_igtf = record.amount + record.tsc_igtf_payment_amount

    def _post_payments(self, to_process, edit_mode=False):
        super(TscAccountPaymentRegister, self)._post_payments(to_process, edit_mode)
        
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
            
        for tsc_payment in payments:
            if tsc_payment.tsc_with_igtf:
                if not tsc_payment.tsc_igtf_payment_journal.id:
                    raise UserError(_('If the payment is linked with IGTF, an IGTF journal is needed to complete this action.'))
                tsc_payment.tsc_create_igtf_move()  
    
    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(TscAccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        res.update({
            'tsc_with_igtf': self.tsc_with_igtf,
            'tsc_igtf_payment_journal': self.tsc_igtf_payment_journal.id,
            'tsc_igtf_payment_amount': self.tsc_igtf_payment_amount,
            'tsc_amount_with_igtf': self.tsc_amount_with_igtf,
        })

        return res
        


