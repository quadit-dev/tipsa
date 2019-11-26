# -*- coding: utf-8 -*-

{
    'name': 'Integración TIPSA SW FACTURA',
    'version': '1',
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
    'views/tipsa_fac_view.xml',
    'views/res_partner_view.xml',
    'views/stock_picking_view.xml',
    'wizard/ws_etiqueta_fac.xml',
    'report/report_etiqueta.xml'
    ],
    'demo': [],
    'installable': True
}
