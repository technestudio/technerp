from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FiscalComplianceConfig(models.Model):
    _name = 'fiscal.compliance.config'
    _description = 'Configuración de Cumplimiento Fiscal'
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)
    fiscal_mode_enabled = fields.Boolean(string='Fiscal Mode Enabled', default=False)
    
    environment = fields.Selection([
        ('test', 'Test'),
        ('homologation', 'Homologation'),
        ('production', 'Production')
    ], string='Environment', default='test', required=True)
    
    seniat_rif = fields.Char(string='SENIAT RIF', related='company_id.vat', readonly=False)
    seniat_authorization_number = fields.Char(string='SENIAT Authorization Number')
    seniat_authorization_date = fields.Date(string='SENIAT Authorization Date')
    
    provider_id = fields.Many2one('fiscal.provider.registry', string='System Provider')
    current_system_version_id = fields.Many2one('fiscal.system.version', string='Current System Version')
    
    allow_offline_mode = fields.Boolean(string='Allow Offline Mode', default=False)
    require_transmission = fields.Boolean(string='Require Transmission', default=True)
    transmission_deadline_hours = fields.Integer(string='Transmission Deadline (Hours)', default=24)
    
    fiscal_document_lock_policy = fields.Selection([
        ('strict', 'Strict (No edits after emission)'),
    ], string='Document Lock Policy', default='strict', required=True)
    
    audit_enabled = fields.Boolean(string='Audit Enabled', default=True)
    hash_enabled = fields.Boolean(string='Hash Enabled', default=True)
    qr_enabled = fields.Boolean(string='QR Enabled', default=True)
    
    last_validation_date = fields.Datetime(string='Last Validation Date')
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Solo puede existir una configuración fiscal activa por compañía.')
    ]

    @api.constrains('fiscal_mode_enabled', 'current_system_version_id')
    def _check_authorized_version(self):
        for record in self:
            if record.fiscal_mode_enabled and record.environment == 'production':
                if not record.current_system_version_id or not record.current_system_version_id.is_authorized_version:
                    raise ValidationError(_('En modo producción, debe utilizar una versión de sistema autorizada.'))
