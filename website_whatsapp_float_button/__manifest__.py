# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Float Button',
    'summary': 'Whatsapp Float Button',
    'version': '1.0',
    "license": "AGPL-3",
    'description': "Whatsapp Float Button",
    'author': 'Utku Halis',
    'support': 'utkuhalis97@gmail.com',
    'category': 'Website',
    'website': "https://utkuhalis.com.tr",
    'depends': ['web', 'website'],
    'price': 10.00,
    'currency': 'EUR',
    'data': [
      "views/templates.xml",
      "views/backend/res_config_settings.xml",
    ],
    'images' : [
      'images/cover.png',
      'static/description/icon.png'
    ],
    'assets': {
      "web.assets_frontend": [
        "website_whatsapp_float_button/static/src/css/whatsapp.css"
      ]
    },
    'installable': True,
    'auto_install': False,
}
