# -*- coding: utf-8 -*-
{
    'name': "Venezuela IGTF & ITF",
    'summary': """
        Unified module for IGTF and ITF transactions and accounting.
    """,
    'description': """
        - Register payments including the IGTF.
        - Generate accounting entries for ITF collections in banking transactions.
        - Connects IGTF entries in bank journals with national currency for ITF.
    """,
    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",
    'category': 'Accounting',
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'images': ['static/description/icon.png'],
    'depends': ['base', 'account'],
    'data': [
        'views/tsc_res_currency_views.xml',
        'views/tsc_res_config_settings_views.xml',
        'views/igtf_account_journal_views.xml',
        'views/itf_account_journal_views.xml',
        'views/igtf_account_payment_views.xml',
        'views/itf_account_payment_views.xml',
        'views/conn_account_payment_views.xml',
        'views/tsc_account_move_views.xml',
        'wizard/igtf_account_payment_register.xml',
        'report/tsc_report_invoice.xml',
        'report/tsc_report_invoice_igtf.xml',
    ],
    'demo': [
    ],
}
