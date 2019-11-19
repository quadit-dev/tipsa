#-*- coding:utf-8 -*-

from openerp import _, api, fields, models


class envio_tipsa(models.Model):
    _name = 'envio.tipsa'
    _description = 'Envio Tipsa'
    #Datos envio ------------ *
    name = fields.Char('Name', required=True)
    albaran = fields.Char('Albaran', required=True)
    agencia_ori = fields.Char('Agencia de Origen', required=True)
    agencia_des = fields.Char('Agencia de Destino', required=True)
    dtm_envio = fields.Datetime ('Fecha envio', readonly = False)
    file = fields.Binary('Etiqueta')
    paq = fields.Char('Número de paquetes')
    datas_fname = fields.Char('File Name', size=256)





