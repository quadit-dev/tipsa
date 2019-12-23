#-*- coding:utf-8 -*-

from openerp import _, api, fields, models


class envio_tipsa(models.Model):
    _name = 'envio.tipsa'
    _description = 'Envio Tipsa'
    #Datos envio ------------ *
    name = fields.Char('Name', required=True)
    albaran = fields.Char('Albaran Tipsa', required=True)
    agencia_ori = fields.Char('Origen', required=True)
    agencia_des = fields.Char('Empresa', required=True)
    dtm_envio = fields.Datetime ('Fecha envio', readonly = False)
    file = fields.Binary('Etiqueta')
    paq = fields.Char('Número de paquetes')
    datas_fname = fields.Char('File Name', size=256)
    albaran_soluziono = fields.Text('Albaranes de referencia')

class servicio_tipsa(models.Model):
    _name = 'servicio.tipsa'
    _description = 'Servicios Tipsa'
    name = fields.Char('Nombre del servicio')
    codigo = fields.Char('Codigo del servicio')





