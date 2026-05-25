{
    'name': 'Venezuela - Fiscal Provider Registry',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Gestión Avanzada de Expedientes Técnicos y PACs (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'license': 'LGPL-3',
    'depends': ['tsc_l10n_ve_fiscal_compliance'],
    'data': [
        'security/ir.model.access.csv',
        'views/fiscal_provider_document_views.xml',
        'views/fiscal_provider_registry_inherit_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
