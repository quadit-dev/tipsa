# -*- coding: utf-8 -*-
from openerp import _, api, fields, models

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    codigo_tipsa = fields.Char('Codigo Tipsa')
    num_home = fields.Char()
    num_piso = fields.Char()
    codigo_provin = fields.Char()
    TipoVia = fields.Selection([('C', 'Calle'),
                                ('PZA', 'Plaza'),
                                ('AV', 'Avenida')],
        string='Tipo de vía',required=True)
