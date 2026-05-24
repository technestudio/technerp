
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import models, fields, api, _


class TscAccountMove(models.Model):
    
    _inherit = 'account.move'
    

    tsc_invoice_date_seniat = fields.Datetime(
        string='Invoice date according to SENIAT requirement',
        help='Invoice date according to SENIAT requirement',
        readonly=True,
        store=True,
        copy=False,
        compute='_compute_tsc_invoice_date_seniat'
    )

    @api.depends('invoice_date')
    def _compute_tsc_invoice_date_seniat(self):
        for record in self:
            if record.invoice_date:
                invoice_date = fields.Date.from_string(record.invoice_date)
                if invoice_date:
                    current_time = datetime.now().time()
                    combined_datetime = datetime.combine(invoice_date, current_time)
                    record.tsc_invoice_date_seniat = combined_datetime
            else:
                record.tsc_invoice_date_seniat = False  
    
    def _get_currency_rate_VES(self):
        for record in self:
            ves_currency = self.env.ref('base.VES', raise_if_not_found=False)
            if ves_currency and record.invoice_date:
                currency = self.env['res.currency.rate'].search([
                    ('currency_id', '=', ves_currency.id),
                    ('name', '<=', record.invoice_date)
                ], order='name desc', limit=1)
                
                if currency:
                    return currency
                else:
                    return self.env['res.currency.rate'].search([
                        ('currency_id', '=', ves_currency.id),
                    ], order='name desc', limit=1)
            else:
                return self.env['res.currency.rate'].search([
                    ('currency_id', '=', record.currency_id.id),
                ], order='name desc', limit=1)  
    

    def _get_currency_rate_VES_payments(self):
        for record in self:
            account_move_pay = record.search([('ref', '=', record.payment_reference)], limit=1)
            account_payment = self.env['account.payment'].search([
                ('move_id', '=', account_move_pay.id)
            ], limit=1)
            
            ves_currency = self.env.ref('base.VES', raise_if_not_found=False)
            
            if ves_currency and account_payment:
                currency = self.env['res.currency.rate'].search([
                    ('currency_id', '=', ves_currency.id),
                    ('name', '<=', account_payment.date)
                ], order='name desc', limit=1)
                
                if currency:
                    return currency
                else: 
                    return self.env['res.currency.rate'].search([
                        ('currency_id', '=', ves_currency.id)
                    ], order='name desc', limit=1)                
            else:
                return self.env['res.currency.rate'].search([
                    ('currency_id', '=', record.currency_id.id),
                ], order='name desc', limit=1)  
            
            
    amount_total_words_VES = fields.Char(
        string="Amount total in words VES",
        compute="_compute_amount_total_words_ves",
    )
    
    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words_ves(self):
        for move in self:
            ves_currency = self.env.ref('base.VES', raise_if_not_found=False)
            
            currency_rate = move._get_currency_rate_VES()
            
            if currency_rate:
                amount = move.amount_total * currency_rate.rate
                move.amount_total_words_VES = ves_currency.amount_to_text(amount).replace(',','')
            
       
    def _validate_VES_currency(self):
        for record in self:
            ves_currency = self.env.ref('base.VES', raise_if_not_found=False)
            if record.currency_id == ves_currency:
                return False
            else:                 
                return True
    
    
    def _check_is_igtf_is_installed(self):
        igft_module = self.env['ir.module.module'].search([('name', '=', 'tsc_igtf'), ('state', '=', 'installed')], limit=1)
        return bool(igft_module)
  
    
    # tsc_freeform_control_number = fields.Char(
    #     string='Free form control number',
    #     help='Freeform control number in which the document was printed',
    #     required=False,
    #     readonly=False,
    #     store=True,
    #     copy=False,
    #     tracking=True
    # )