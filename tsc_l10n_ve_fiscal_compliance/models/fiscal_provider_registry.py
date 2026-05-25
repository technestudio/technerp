from odoo import models, fields

class FiscalProviderRegistry(models.Model):
    _name = 'fiscal.provider.registry'
    _description = 'Registro de Proveedor Fiscal SENIAT'
    
    name = fields.Char(string='Provider Name', required=True)
    rif = fields.Char(string='RIF', required=True)
    legal_name = fields.Char(string='Legal Name', required=True)
    contact_name = fields.Char(string='Contact Name')
    contact_email = fields.Char(string='Contact Email')
    contact_phone = fields.Char(string='Contact Phone')
    address = fields.Text(string='Address')
    
    authorization_number = fields.Char(string='Authorization Number')
    authorization_date = fields.Date(string='Authorization Date')
    authorization_status = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revoked', 'Revoked'),
        ('suspended', 'Suspended')
    ], string='Authorization Status', default='draft')
    
    technical_manual_attachment_id = fields.Many2one('ir.attachment', string='Technical Manual')
    user_manual_attachment_id = fields.Many2one('ir.attachment', string='User Manual')
    
    platform_description = fields.Text(string='Platform Description')
    database_description = fields.Text(string='Database Description')
    application_description = fields.Text(string='Application Description')
    audit_monitor_description = fields.Text(string='Audit Monitor Description')
