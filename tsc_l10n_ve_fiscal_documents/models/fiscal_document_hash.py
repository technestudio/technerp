import hashlib
from odoo import models, fields, api

class FiscalDocumentHash(models.Model):
    _name = 'fiscal.document.hash'
    _description = 'Registro de Hashes Fiscales (Anti-Alteración)'
    
    name = fields.Char(string='Document Name', required=True)
    model_name = fields.Char(string='Model', required=True)
    record_id = fields.Integer(string='Record ID', required=True)
    hash_value = fields.Char(string='SHA-256 Hash', required=True)
    previous_hash_id = fields.Many2one('fiscal.document.hash', string='Previous Hash')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model
    def create_hash(self, model_name, record_id, payload):
        # Generar hash seguro basado en payload
        hash_obj = hashlib.sha256()
        hash_obj.update(payload.encode('utf-8'))
        computed_hash = hash_obj.hexdigest()
        
        # Buscar el hash anterior para encadenamiento (Blockchain-like)
        last_hash = self.search([('company_id', '=', self.env.company.id)], order='id desc', limit=1)
        
        return self.create({
            'name': f"Hash for {model_name} ID {record_id}",
            'model_name': model_name,
            'record_id': record_id,
            'hash_value': computed_hash,
            'previous_hash_id': last_hash.id if last_hash else False,
            'company_id': self.env.company.id
        })
