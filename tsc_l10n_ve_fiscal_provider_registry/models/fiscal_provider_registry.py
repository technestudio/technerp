from odoo import models, fields

class FiscalProviderRegistry(models.Model):
    _inherit = 'fiscal.provider.registry'

    document_ids = fields.One2many('fiscal.provider.document', 'provider_id', string='Expediente Técnico')
    contract_start_date = fields.Date(string='Inicio del Contrato')
    contract_end_date = fields.Date(string='Fin del Contrato')
    support_email = fields.Char(string='Email de Soporte Técnico')
    api_endpoint_url = fields.Char(string='API Endpoint Base URL')
    api_version = fields.Char(string='API Version')
