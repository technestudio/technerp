from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import hashlib
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    fiscal_document_number = fields.Char(string='Fiscal Document Number', copy=False, tracking=True)
    fiscal_control_number = fields.Char(string='Fiscal Control Number', copy=False, tracking=True)
    
    fiscal_hash = fields.Char(string='Fiscal Hash', copy=False, readonly=True)
    fiscal_previous_hash = fields.Char(string='Previous Fiscal Hash', copy=False, readonly=True)
    
    fiscal_qr_payload = fields.Text(string='QR Payload', copy=False)
    fiscal_qr_image = fields.Binary(string='QR Image', copy=False)
    
    fiscal_issued_at = fields.Datetime(string='Fiscal Issued At', copy=False)
    fiscal_locked = fields.Boolean(string='Fiscal Locked', default=False, copy=False)
    
    fiscal_status = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('transmitted', 'Transmitted'),
        ('transmission_failed', 'Transmission Failed'),
        ('cancelled', 'Cancelled'),
        ('corrected', 'Corrected')
    ], string='Fiscal Status', default='draft', copy=False, tracking=True)
    
    fiscal_transmission_state = fields.Selection([
        ('not_required', 'Not Required'),
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed')
    ], string='Transmission State', default='not_required', copy=False, tracking=True)
    
    fiscal_original_move_id = fields.Many2one('account.move', string='Original Document', copy=False)
    fiscal_integrity_verified = fields.Boolean(string='Integrity Verified', default=True, copy=False)
    fiscal_integrity_last_check = fields.Datetime(string='Last Integrity Check', copy=False)

    def _compute_fiscal_hash_payload(self):
        self.ensure_one()
        payload_dict = {
            'company_vat': self.company_id.vat or '',
            'partner_vat': self.partner_id.vat or '',
            'fiscal_document_number': self.fiscal_document_number or '',
            'invoice_date': str(self.invoice_date) if self.invoice_date else '',
            'amount_untaxed': self.amount_untaxed,
            'amount_tax': self.amount_tax,
            'amount_total': self.amount_total,
            'currency_name': self.currency_id.name or '',
            'move_type': self.move_type,
            'internal_id': self.id
        }
        return json.dumps(payload_dict, sort_keys=True)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            config = self.env['fiscal.compliance.config'].search([
                ('company_id', '=', move.company_id.id),
                ('active', '=', True),
                ('fiscal_mode_enabled', '=', True)
            ], limit=1)
            
            if config and move.move_type in ('out_invoice', 'out_refund'):
                if not move.fiscal_document_number:
                    move.fiscal_document_number = move.name  # Fallback to internal name initially
                
                move.fiscal_issued_at = fields.Datetime.now()
                
                if config.hash_enabled:
                    payload = move._compute_fiscal_hash_payload()
                    hash_record = self.env['fiscal.document.hash'].create_hash(move._name, move.id, payload)
                    move.fiscal_hash = hash_record.hash_value
                    if hash_record.previous_hash_id:
                        move.fiscal_previous_hash = hash_record.previous_hash_id.hash_value

                move.fiscal_locked = True
                move.fiscal_status = 'issued'
                
                if config.require_transmission:
                    move.fiscal_transmission_state = 'pending'
                    # Integration will pick this up
        return res

    def button_cancel(self):
        for move in self:
            if move.fiscal_locked:
                raise UserError(_("No puede cancelar un documento que ya ha sido emitido fiscalmente. Debe emitir una Nota de Crédito."))
        return super(AccountMove, self).button_cancel()

    def button_draft(self):
        for move in self:
            if move.fiscal_locked:
                raise UserError(_("No puede regresar a borrador un documento fiscal ya emitido y bloqueado."))
        return super(AccountMove, self).button_draft()

    @api.ondelete(at_uninstall=False)
    def _unlink_except_fiscal_locked(self):
        for move in self:
            if move.fiscal_locked:
                raise UserError(_("Está estrictamente prohibido eliminar documentos fiscales emitidos."))

    def write(self, vals):
        for move in self:
            if move.fiscal_locked:
                critical_fields = ['partner_id', 'invoice_date', 'move_type', 'currency_id', 'amount_total', 'fiscal_document_number', 'fiscal_hash']
                if any(field in vals for field in critical_fields):
                    raise UserError(_("No se pueden modificar campos críticos de un documento fiscal emitido."))
        return super(AccountMove, self).write(vals)

    def verify_fiscal_integrity(self):
        for move in self:
            if not move.fiscal_hash:
                continue
            payload = move._compute_fiscal_hash_payload()
            hash_obj = hashlib.sha256()
            hash_obj.update(payload.encode('utf-8'))
            computed_hash = hash_obj.hexdigest()
            
            move.fiscal_integrity_last_check = fields.Datetime.now()
            if computed_hash != move.fiscal_hash:
                move.fiscal_integrity_verified = False
                # Aquí se debería crear un evento de auditoría en el módulo tsc_l10n_ve_fiscal_audit
            else:
                move.fiscal_integrity_verified = True
