# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TscResCurrency(models.Model):

    _inherit = 'res.currency'

    tsc_apply_IGTF = fields.Boolean(string="Apply IGTF for payments on this currency?",
                                    help="Identifies if payments registered in this currency will have to apply the IGTF.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    default=False,
                                    company_dependent=True)

    @api.onchange('active')
    def tsc_active_status(self):
        for record in self:
            if not record.active:
                record.tsc_apply_IGTF = False
