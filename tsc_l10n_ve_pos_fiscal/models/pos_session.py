from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    fiscal_document_count = fields.Integer(string='Documentos Fiscales Emitidos', compute='_compute_fiscal_summary')
    fiscal_total_sales = fields.Monetary(string='Ventas Fiscales', compute='_compute_fiscal_summary')
    fiscal_total_tax = fields.Monetary(string='Impuestos Fiscales', compute='_compute_fiscal_summary')
    fiscal_transmission_pending_count = fields.Integer(string='Pendientes por Transmitir', compute='_compute_fiscal_summary')
    fiscal_closing_hash = fields.Char(string='Hash de Cierre Fiscal', copy=False, readonly=True)

    def _compute_fiscal_summary(self):
        for session in self:
            orders = session.order_ids.filtered(lambda o: o.fiscal_locked)
            session.fiscal_document_count = len(orders)
            session.fiscal_total_sales = sum(orders.mapped('amount_total'))
            session.fiscal_total_tax = sum(orders.mapped('amount_tax'))
            session.fiscal_transmission_pending_count = len(orders.filtered(lambda o: o.fiscal_transmission_state == 'pending'))

    def action_pos_session_close(self, balancing_account=False):
        res = super().action_pos_session_close(balancing_account=balancing_account)
        for session in self:
            config = self.env['fiscal.compliance.config'].search([
                ('company_id', '=', session.company_id.id),
                ('active', '=', True),
                ('fiscal_mode_enabled', '=', True)
            ], limit=1)
            
            if config and config.hash_enabled:
                import hashlib
                import json
                payload_dict = {
                    'session_id': session.id,
                    'fiscal_document_count': session.fiscal_document_count,
                    'fiscal_total_sales': session.fiscal_total_sales,
                    'fiscal_total_tax': session.fiscal_total_tax,
                }
                payload = json.dumps(payload_dict, sort_keys=True)
                hash_record = self.env['fiscal.document.hash'].create_hash(session._name, session.id, payload)
                session.fiscal_closing_hash = hash_record.hash_value
                
        return res
