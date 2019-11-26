# -*- coding: utf-8 -*-

{
    'name': 'Integración TIPSA SW',
    'version': '9.0.1.0.0',
    'depends': [
        'stock',
        'account',
        'mail',
        'sale',
        'purchase',
        'tqn_partnerdiscount',
        'shipping_eci_corte_ingles',
        'tipsa_envios'
    ],
    'author': 'Quadit, S.A. de C.V.',
    'description': 'Integración de TIPSA',
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
