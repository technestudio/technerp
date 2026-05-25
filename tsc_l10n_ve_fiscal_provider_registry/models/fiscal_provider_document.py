from odoo import models, fields, api

class FiscalProviderDocument(models.Model):
    _name = 'fiscal.provider.document'
    _description = 'Expediente Técnico del Proveedor'
    _order = 'date desc'
    
    name = fields.Char(string='Document Name', required=True)
    provider_id = fields.Many2one('fiscal.provider.registry', string='Proveedor', required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('technical_specs', 'Especificaciones Técnicas'),
        ('seniat_authorization', 'Certificado de Autorización SENIAT'),
        ('contract', 'Contrato de Servicio'),
        ('sla', 'SLA (Acuerdo de Nivel de Servicio)'),
        ('other', 'Otro')
    ], string='Tipo de Documento', required=True)
    
    date = fields.Date(string='Fecha del Documento', default=fields.Date.context_today)
    expiry_date = fields.Date(string='Fecha de Vencimiento')
    file = fields.Binary(string='Archivo', attachment=True, required=True)
    file_name = fields.Char(string='File Name')
    notes = fields.Text(string='Notas')
    active = fields.Boolean(default=True)
