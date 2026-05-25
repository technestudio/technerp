from odoo import models, fields

class FiscalValidationRule(models.Model):
    _name = 'fiscal.validation.rule'
    _description = 'Reglas de Validación Fiscal'
    
    name = fields.Char(string='Rule Name', required=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    condition_python = fields.Text(string='Condition (Python)')
    error_message = fields.Char(string='Error Message', required=True)
    severity = fields.Selection([
        ('warning', 'Warning'),
        ('blocker', 'Blocker')
    ], string='Severity', default='blocker')
