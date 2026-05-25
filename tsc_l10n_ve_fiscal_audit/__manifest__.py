{
    'name': 'Venezuela - Bitácora de auditoría fiscal SENIAT',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Bitácora y Auditoría de Eventos Fiscales (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'license': 'LGPL-3',
    'depends': ['tsc_l10n_ve_fiscal_compliance'],
    'data': [
        'security/ir.model.access.csv',
        'views/fiscal_event_log_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
