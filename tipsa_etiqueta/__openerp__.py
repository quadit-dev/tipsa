# -*- coding: utf-8 -*-
# Copyright 2019 QUADIT https://www.quadit.mx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Integración TIPSA SW',
    'version': '9.0.1.0.0',
    'depends': [
        'stock',
        'account',
        'mail',
        'sale',
        'purchase',
        'tipsa_envios'
    ],
    'author': 'Quadit, S.A. de C.V.',
    'description': 'Integración con TIPSA',
    'website': 'https://www.quadit.mx',
    'data': [
        'security/tipsa_etiqueta_security.xml',
        'security/ir.model.access.csv',
        'views/integracion.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_view.xml',
        'wizard/ws_etiqueta.xml',
        'report/report_etiqueta.xml'
    ],
    'demo': [],
    'installable': True
}
