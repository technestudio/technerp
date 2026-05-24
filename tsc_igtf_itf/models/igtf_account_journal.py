# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountJournal(models.Model):

    _inherit = 'account.journal'

    tsc_is_igtf_journal = fields.Boolean(string="Will it receive IGTF payments?",
                                    help="Determines if IGTF payments will be recorded through this journal.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    tracking=True,
                                    default=False)

    tsc_igtf_account = fields.Many2one(string="Payable Account",
                                    comodel_name="account.account",
                                    help="Account payable in which the IGTF received is recorded.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    tracking=True,
                                    default=False,
                                    domain="[('id','in',tsc_igtf_account_helper)]")

    tsc_igtf_account_helper = fields.Many2many(comodel_name="account.account", 
                                               string='Filtered Accounts',
                                               store=False, readonly=False,
                                               compute='tsc_compute_igtf_account_helper')

    tsc_igtf_percentage = fields.Float(string='% IGTF',
                                       help="IGTF percentage to apply.",
                                       required=False,
                                       store=True, 
                                       readonly=False,
                                       copy=True,
                                       tracking=True,
                                       default=1.00)

    tsc_igtf_expense = fields.Many2one(string="Expense account",
                                    comodel_name="account.account",
                                    help="Expense account in which the IGTF paid is recorded.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    tracking=True,
                                    default=False,
                                    domain="[('id','in',tsc_igtf_expense_helper)]")

    tsc_igtf_expense_helper = fields.Many2many(comodel_name="account.account", 
                                               string='Filtered Expenses Accounts',
                                               store=False, readonly=False,
                                               compute='tsc_compute_igtf_expense_account_helper')

    @api.depends('tsc_is_igtf_journal')
    def tsc_compute_igtf_account_helper(self):
        for record in self:
            record.tsc_igtf_account_helper = self.env['account.account'].search([
            ('deprecated','=',False),
            ('company_id', '=', self.env.company.id),
            '|',
            ('account_type','=','liability_payable'),
            ('account_type','=','liability_current'),
            ])

    @api.depends('tsc_is_igtf_journal')
    def tsc_compute_igtf_expense_account_helper(self):
        for record in self:
            record.tsc_igtf_expense_helper = self.env['account.account'].search([
            ('deprecated','=',False),
            ('company_id', '=', self.env.company.id),
            ('account_type','=','expense'),
            ])

    @api.constrains('tsc_igtf_percentage')
    def tsc_check_igtf_percentage(self):
        for record in self:
            if record.tsc_igtf_percentage <= 0.00 or record.tsc_igtf_percentage > 100.00:
                raise ValidationError(_("The field % IGTF only allows values higher than 0.00% and values equal or lower than 100%"))








