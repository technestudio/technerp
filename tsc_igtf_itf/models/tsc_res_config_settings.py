# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TscResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    tsc_igtf_text = fields.Html(string="IGTF text for invoices",
                                    help="The indicated text will appear on customer invoices.",
                                    required=False,
                                    readonly=False,
                                    store=True,
                                    copy=True,
                                    translate=True)

    @api.model
    def get_values(self):
        res = super(TscResConfigSettings, self).get_values()
        res.update(
            tsc_igtf_text = self.env['ir.config_parameter'].sudo().get_param('tsc_igtf_itf.tsc_igtf_text'),
        )
        return res

    def set_values(self):
        res = super(TscResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('tsc_igtf_itf.tsc_igtf_text', self.tsc_igtf_text or "")
        return res