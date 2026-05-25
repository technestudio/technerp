{
    'name': 'Venezuela - POS Fiscal',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale/Localizations',
    'summary': 'Extensión Fiscal para Punto de Venta (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'tsc_l10n_ve_fiscal_documents', 'tsc_l10n_ve_seniat_integration'],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
