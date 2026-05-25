{
    'name': 'Venezuela - Punto de venta (POS) fiscal SENIAT',
    'category': 'Point of Sale/Localizations',
    'summary': 'Extensión Fiscal para Punto de Venta (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'description': """
        - Bloqueo de alteraciones en Punto de Venta (POS) y consolidación fiscal (Reporte Z).
    """,
    'website': "https://technestudioit.com/",
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'depends': ['point_of_sale', 'tsc_l10n_ve_fiscal_documents', 'tsc_l10n_ve_seniat_integration'],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
