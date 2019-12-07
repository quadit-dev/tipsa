# -*- coding: utf-8 -*-
# Copyright 2019 QUADIT https://www.quadit.mx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import _, api, fields, models


class tipsa_servicio(models.Model):
    _name = 'tipsa.servicio'
    _description = 'Integracion'
    name = fields.Char('Nombre del servicio')
    url_login = fields.Char('URL login', required=True)
    url_accion = fields.Char('URL accion', required=True)
    agencia = fields.Char('Agencia')
    user = fields.Char('Usuario', required=True)
    password = fields.Char('Contraseña', required=True)
