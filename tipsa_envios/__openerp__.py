# -*- coding: utf-8 -*-

{
    'name': 'Envio TIPSA SW',
    'version': '9.0.1.0.0',
    'depends': [
        'stock',
        'account',
        'mail',
        'sale',
        'purchase',
    ],
    'author': 'Quadit, S.A. de C.V.',
    'description': 'Integración de TIPSA',
    'website': 'https://www.quadit.mx',
    'data': [
    'views/envio_tipsa_view.xml',
    'report/report_envio_etiqueta.xml',
    'data/servicio.tipsa.csv'
    ],
    'demo': [],
    'installable': True
}
