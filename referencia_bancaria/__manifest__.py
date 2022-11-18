# -*- coding: utf-8 -*-
{
    'name': "Bank Reference for Payments",
    'summary': "This application allow specifying a bank reference associated with a payment, validating that it is not used for several payments.",
    "description": """
        This application includes a unique reference number for payments made by bank (transfers, zelle, etc.).
    """,
    'author': "Techne Studio IT & Consulting",
    'website': "http://www.technerp.com",
    'category': 'account',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['account','sale_management'],
    'price': 35.00,
    'currency': "USD",
    'data': [
        'views/account_payment_register_views.xml',
        'views/account_payment_views.xml',
    ],
    "images":['static/description/referencia_bancaria_unica.gif'],
    'assets': {
        'web.assets_backend': [
            'referencia_bancaria/static/src/js/javaScript.js',
            'referencia_bancaria/static/src/css/style.scss',
        ]
    }
}
