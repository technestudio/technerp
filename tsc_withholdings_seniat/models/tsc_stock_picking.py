# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TscStockPicking(models.Model):
    
    _inherit = 'stock.picking'
    
    tsc_control_number_free_form = fields.Char(
        string='Control number free form',
        help='To have control, indicate the free form number used when printing this Dispatch Guide',
        required=False,
        readonly=False,
        store=True,
        copy=True,
        tracking=True
    )
    
    tsc_control_number_manual = fields.Char(
        string='Control number manual',
        help='Control number for printing Dispatch Guides with letterhead. This number will be reflected on the print',
        required=False,
        readonly=False,
        store=True,
        copy=False,
        tracking=True
    )


    @api.constrains('tsc_control_number_manual')
    def _check_tsc_control_number_manual(self):
        for record in self:
            if record.tsc_control_number_manual:
                if len(record.tsc_control_number_manual) != 6:
                    raise ValidationError(_('The Control number manual must be exactly 6 characters long.'))
                if self.search_count([('tsc_control_number_manual', '=', record.tsc_control_number_manual)]) > 1:
                    raise ValidationError(_('The Control number manual must be unique.'))
      
          
    tsc_reason_transfer = fields.Text(
        string='Reason for transfer',
        help='Optional information for Dispatch Guides, about the reason for the transfer',
        required=False,
        readonly=False,
        store=True,
        copy=True,
        tracking=True
    )
    
    tsc_currency_dispatch_note = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        help='Currency in which the total of the merchandise included in the Dispatch Guide will be expressed',
        required=False,
        readonly=False,
        store=True,
        copy=True,
        tracking=True,
        default=lambda self: self.env.ref('base.VES', raise_if_not_found=False) and self.env.ref('base.VES').id or False
    )
    
    tsc_exchange_rate_dispatche_note = fields.Float(
        string='Exchange rate',
        help='Exchange rate according to the effective date of the Dispatch Note',
        required=False,
        readonly=True,
        store=True,
        copy=False
    )
    
    @api.constrains('state', 'tsc_currency_dispatch_note', 'date_done')
    def _check_exchange_rate_on_done_state(self):
        for record in self:
            if record.state == 'done' and record.tsc_currency_dispatch_note and record.date_done:
                for rate in record.tsc_currency_dispatch_note.rate_ids:
                    rate_date = datetime.combine(rate.name, datetime.min.time())
                    if rate_date <= record.date_done:
                        record.tsc_exchange_rate_dispatche_note = rate.company_rate
                        break
            else:
                record.tsc_exchange_rate_dispatche_note = 0.0
