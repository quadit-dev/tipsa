#-*- coding:utf-8 -*-

from openerp import _, api, fields, models

class tipsa_servicio_fac(models.Model):
    _name = 'tipsa.servicio.fac'
    _description = 'Integracion'
    name = fields.Char('Nombre del servicio')
    url_login = fields.Char('URL login', required=True)
    url_accion = fields.Char('URL accion', required=True)
    agencia = fields.Char('Agencia')
    user = fields.Char('Usuario', required=True)
    password = fields.Char('Contraseña', required=True)
