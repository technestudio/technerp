# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TscIrActionReport(models.Model):
    
    _inherit = 'ir.actions.report'
    
    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        
        reports_name = ['tsc_withholdings_seniat.tsc_factura_bs', 
                        'tsc_withholdings_seniat.tsc_factura_bs_sin_pagos',
                        'tsc_withholdings_seniat.tsc_factura_bs_fl',
                        'tsc_withholdings_seniat.tsc_factura_bs_fl_sin_pagos',
                        'tsc_withholdings_seniat.tsc_factura_con_tasa',
                        'tsc_withholdings_seniat.tsc_factura_con_tasa_sin_pagos',
                        'tsc_withholdings_seniat.tsc_factura_con_tasa_fl',
                        'tsc_withholdings_seniat.tsc_factura_con_tasa_fl_sin_pagos']
        
        if self._get_report(report_ref).report_name in reports_name:
            invoices = self.env['account.move'].browse(res_ids)
            if any(x.move_type in ['in_invoice', 'entry'] for x in invoices):
                raise UserError(_("This print option is not available for this document"))
        
        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)