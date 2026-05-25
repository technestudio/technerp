{
    'name': 'Venezuela - Bitácora de auditoría fiscal SENIAT',
    'category': 'Accounting/Localizations',
    'summary': 'Bitácora y Auditoría de Eventos Fiscales (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'description': """
        - Bitácora de seguridad y auditoría de eventos inmutables para inspectores del SENIAT.
    """,
    'website': "https://technestudioit.com/",
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'depends': ['tsc_l10n_ve_fiscal_compliance'],
    'data': [
        'security/ir.model.access.csv',
        'views/fiscal_event_log_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
