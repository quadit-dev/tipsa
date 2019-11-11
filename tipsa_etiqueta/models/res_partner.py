# -*- coding: utf-8 -*-
from openerp import _, api, fields, models

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    codigo_tipsa = fields.Char('Codigo Tipsa')
