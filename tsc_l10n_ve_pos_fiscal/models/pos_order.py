from odoo import models, fields, api, _
from odoo.exceptions import UserError
import hashlib
import json

class PosOrder(models.Model):
    _inherit = 'pos.order'

    fiscal_document_number = fields.Char(string='Fiscal Document Number', copy=False, readonly=True)
    fiscal_hash = fields.Char(string='Fiscal Hash', copy=False, readonly=True)
    fiscal_status = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
    ], string='Fiscal Status', default='draft', copy=False)
    fiscal_transmission_state = fields.Selection([
        ('not_required', 'Not Required'),
        ('pending', 'Pending'),
    ], string='Transmission State', default='not_required', copy=False)
    fiscal_issued_at = fields.Datetime(string='Fiscal Issued At', copy=False)
    fiscal_locked = fields.Boolean(string='Fiscal Locked', default=False, copy=False)

    def _compute_fiscal_hash_payload(self):
        self.ensure_one()
        payload_dict = {
            'company_vat': self.company_id.vat or '',
            'partner_vat': self.partner_id.vat if self.partner_id else 'Consumidor Final',
            'fiscal_document_number': self.fiscal_document_number or '',
            'date_order': str(self.date_order) if self.date_order else '',
            'amount_total': self.amount_total,
            'amount_tax': self.amount_tax,
            'currency_name': self.currency_id.name or '',
            'internal_id': self.id
        }
        return json.dumps(payload_dict, sort_keys=True)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            config = self.env['fiscal.compliance.config'].search([
                ('company_id', '=', order.company_id.id),
                ('active', '=', True),
                ('fiscal_mode_enabled', '=', True)
            ], limit=1)
            
            if config:
                order.fiscal_document_number = order.pos_reference or order.name
                order.fiscal_issued_at = fields.Datetime.now()
                
                if config.hash_enabled:
                    payload = order._compute_fiscal_hash_payload()
                    hash_record = self.env['fiscal.document.hash'].create_hash(order._name, order.id, payload)
                    order.fiscal_hash = hash_record.hash_value

                order.fiscal_locked = True
                order.fiscal_status = 'issued'
                if config.require_transmission:
                    order.fiscal_transmission_state = 'pending'
        return orders

    @api.ondelete(at_uninstall=False)
    def _unlink_except_fiscal_locked(self):
        for order in self:
            if order.fiscal_locked:
                raise UserError(_("Está estrictamente prohibido eliminar órdenes POS fiscalizadas."))

    def write(self, vals):
        for order in self:
            if order.fiscal_locked:
                critical_fields = ['partner_id', 'amount_total', 'amount_tax', 'lines', 'fiscal_document_number', 'fiscal_hash']
                if any(field in vals for field in critical_fields):
                    raise UserError(_("No se pueden modificar campos críticos de una orden POS fiscalizada."))
        return super(PosOrder, self).write(vals)
