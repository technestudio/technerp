# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class TscAccountMove(models.Model):

    _inherit = 'account.move'

    tsc_itf_move_id = fields.Many2one(comodel_name='account.move',
                                       string='ITF Journal Entry',
                                       required=False, 
                                       store=True,
                                       readonly=True,
                                       check_company=True,
                                       copy=False)

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