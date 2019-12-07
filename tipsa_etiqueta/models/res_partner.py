# -*- coding: utf-8 -*-
# Copyright 2019 QUADIT https://www.quadit.mx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import _, api, fields, models


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    num_home = fields.Char()
    num_piso = fields.Char()
    codigo_provin = fields.Char()
    TipoVia = fields.Selection([
        ('C', 'Calle'),
        ('PZA', 'Plaza'),
        ('AV', 'Avenida')],
        string='Tipo de vía')
