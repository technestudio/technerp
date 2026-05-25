{
    'name': 'Venezuela - Integración y transmisión de datos SENIAT',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Cola de transmisión y API Adapter para facturación electrónica (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'license': 'LGPL-3',
    'depends': ['tsc_l10n_ve_fiscal_documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/fiscal_transmission_queue_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
