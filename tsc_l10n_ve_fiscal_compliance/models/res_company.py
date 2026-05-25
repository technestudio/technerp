from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fiscal_compliance_config_id = fields.Many2one(
        'fiscal.compliance.config', 
        string='Configuración Fiscal',
        compute='_compute_fiscal_compliance_config_id'
    )
    
    def _compute_fiscal_compliance_config_id(self):
        for company in self:
            config = self.env['fiscal.compliance.config'].search([
                ('company_id', '=', company.id),
                ('active', '=', True)
            ], limit=1)
            company.fiscal_compliance_config_id = config
