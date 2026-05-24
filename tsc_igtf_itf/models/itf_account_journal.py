# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountJournal(models.Model):

    _inherit = 'account.journal'

    tsc_generate_ITF = fields.Boolean(string="Generate ITF accounting entry",
                                    help="Determines if making payments with this journal will generate an accounting entry for ITF.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    tracking=True,
                                    default=False)

    @api.depends('tsc_generate_ITF')
    def tsc_compute_itf_account_helper(self):
        for record in self:
            record.tsc_itf_account_helper = self.env['account.account'].search([
                ('deprecated','=',False),
                ('company_id', '=', self.env.company.id),
                ('account_type','=','expense'),
            ])

    tsc_itf_account_helper = fields.Many2many(comodel_name="account.account",
                                                      string='Filtered Accounts',
                                                      store=False, readonly=False,
                                                      compute="tsc_compute_itf_account_helper")

    tsc_ITF_account_expense = fields.Many2one(string="Expenditure account by ITF",
                                    comodel_name="account.account",
                                    help="Expense account in which the ITF is recorded.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    tracking=True,
                                    default=False,
                                    domain="[('id','in',tsc_itf_account_helper)]")

    tsc_itf_percentage = fields.Float(string='% ITF',
                                       help="ITF percentage to apply.",
                                       required=False,
                                       store=True, 
                                       readonly=False,
                                       copy=True,
                                       tracking=True,
                                       default=1.00)

    @api.constrains('tsc_itf_percentage')
    def tsc_check_itf_percentage(self):
        for record in self:            
            if (record.tsc_generate_ITF 
                and (record.tsc_itf_percentage <= 0.00
                     or record.tsc_itf_percentage > 100.00)
               ):
                raise ValidationError(_("The field % ITF only allows values higher than 0.00% and values equal or lower than 100%"))








