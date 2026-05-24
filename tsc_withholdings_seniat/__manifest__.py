# -*- coding: utf-8 -*-
{
    'name': "Venezuelan Withholdings and SENIAT Formats",
    'summary': """
        Unified module for VAT/ISLR withholdings, SENIAT exports, and compliant report formats.
    """,
    'description': """
        - Configure and generate VAT and ISLR withholdings.
        - Generate ISLR and VAT withholding files to be sent to SENIAT.
        - Modifies reports of Customer Invoices, Credit Notes, Debit Notes and Dispatch Guides for SENIAT compliance.
    """,
    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",
    'license': "Other proprietary",
    'category': 'Accounting',
    'version': '19.0.1.0.0',
    'depends': ['base', 'account', 'purchase', 'account_debit_note', 'stock', 'stock_delivery', 'account_accountant', 'account_edi'],
    'data': [
        'security/ir.model.access.csv',
        'data/template_export_data.xml',
        'views/tax_withholdings_views.xml',
        'views/tax_withholdings_templates.xml',
        'views/export_views.xml',
        'views/export_templates.xml',
        'views/formats_views.xml',
        'views/formats_templates.xml',
        'views/report_templates.xml',
        'views/tsc_stock_picking_views.xml',
        'report/tax_withholding_reports.xml',
        'report/tax_withholding_templates.xml',
        'report/tsc_stock_report_views.xml',
        'report/tsc_stock_report_dispatch_note.xml',
        'report/tsc_account_move.xml',
        'report/tsc_account_move_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
