{
    'name': 'Venezuela - Motor de documentos fiscales SENIAT',
    'category': 'Accounting/Localizations',
    'summary': 'Motor de Documentos Fiscales y Control de Hash (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'description': """
        - Control de inalterabilidad para documentos de facturación y firmas Hash criptográficas.
    """,
    'website': "https://technestudioit.com/",
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'depends': ['account', 'tsc_l10n_ve_fiscal_compliance'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
