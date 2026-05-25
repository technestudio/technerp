{
    'name': 'Venezuela - Core de cumplimiento fiscal SENIAT',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Módulo base de configuración y cumplimiento fiscal SENIAT (Providencia SNAT/2024/000121)',
    'author': "Techne Studio IT & Consulting",
    'description': """
        - Configuración base de parámetros fiscales y control de versiones del sistema (Providencia SNAT/2024/000121).
    """,
    'website': "https://technestudioit.com/",
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'depends': ['base', 'account'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/fiscal_compliance_config_views.xml',
        'views/fiscal_provider_registry_views.xml',
        'views/fiscal_system_version_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
