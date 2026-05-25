from odoo import models, fields, api

class FiscalEventLog(models.Model):
    _name = 'fiscal.event.log'
    _description = 'Bitácora de Eventos Fiscales'
    _order = 'create_date desc'
    
    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    event_type = fields.Selection([
        ('config_change', 'Cambio de Configuración Fiscal'),
        ('document_issue', 'Emisión de Documento Fiscal'),
        ('transmission_success', 'Transmisión Exitosa'),
        ('transmission_error', 'Error en Transmisión'),
        ('integrity_failure', 'Falla de Integridad (Hash Inválido)'),
        ('access_violation', 'Intento de Violación de Acceso Fiscal')
    ], string='Tipo de Evento', required=True)
    
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user, readonly=True)
    model_name = fields.Char(string='Modelo Afectado', readonly=True)
    record_id = fields.Integer(string='ID de Registro', readonly=True)
    description = fields.Text(string='Descripción del Evento', readonly=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, readonly=True)
    
    @api.depends('event_type', 'create_date')
    def _compute_name(self):
        for record in self:
            record.name = f"AUDIT-{record.id or 'NEW'}-{record.event_type}"

    @api.model
    def log_event(self, event_type, description, model_name=False, record_id=False):
        return self.create({
            'event_type': event_type,
            'description': description,
            'model_name': model_name,
            'record_id': record_id
        })
