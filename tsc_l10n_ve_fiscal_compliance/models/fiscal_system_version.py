from odoo import models, fields

class FiscalSystemVersion(models.Model):
    _name = 'fiscal.system.version'
    _description = 'Versión del Sistema Fiscal'
    
    name = fields.Char(string='Name', required=True)
    version = fields.Char(string='Version', required=True)
    module_list = fields.Text(string='Module List')
    git_commit_hash = fields.Char(string='Git Commit Hash')
    release_date = fields.Date(string='Release Date')
    
    is_authorized_version = fields.Boolean(string='Is Authorized Version', default=False)
    authorization_reference = fields.Char(string='Authorization Reference')
    
    changelog = fields.Text(string='Changelog')
    checksum = fields.Char(string='Checksum')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_authorization', 'Pending Authorization'),
        ('authorized', 'Authorized'),
        ('deprecated', 'Deprecated'),
        ('revoked', 'Revoked')
    ], string='State', default='draft')
