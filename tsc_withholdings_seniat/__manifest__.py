# -*- coding: utf-8 -*-
{
    'name': "Venezuela Retenciones SENIAT",
    'summary': """
        Módulo unificado para retenciones de IVA e ISLR, exportaciones SENIAT y formatos de informes conformes.
    """,
    'description': """
        - Configurar y generar retenciones de IVA e ISLR.
        - Generar archivos de retención de ISLR e IVA para ser enviados al SENIAT.
        - Modifica los informes de facturas de clientes, notas de crédito, notas de débito y guías de remisión para cumplir con el SENIAT.
    """,
    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",
    'license': "OPL-1",
    'price': 250.0,
    'currency': 'USD',
    'support': 'info@technestudioit.com',
    'images': ['static/description/icon.png'],
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
