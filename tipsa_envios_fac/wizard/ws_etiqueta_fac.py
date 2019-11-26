# -*- coding: utf-8 -*-

from openerp import _, api, fields, models
import requests
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from suds.transport.http import HttpAuthenticated
from suds.client import Client
import base64
from lxml import etree, objectify
from xml.dom import minidom
from datetime import datetime
from openerp.exceptions import UserError, ValidationError
from xml.etree.ElementTree import XML, fromstring, tostring, parse

class servicio_tipsa(models.Model):
    _name = 'servicio.tipsa'
    _inherit = 'servicio.tipsa'


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'


class StockPackOperation(models.Model):
    _name = 'stock.pack.operation'
    _inherit = 'stock.pack.operation'


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'



class ws_etiqueta_fac(models.Model):
    _name = 'ws.etiqueta.fac'
    _description = 'Datos para etiqueta'
    opcion = fields.Many2one('tipsa.servicio',string="Opcion")
    name_env =fields.Char('Nombre envio')
    dtm_envio = fields.Datetime ('Fecha envio',
        readonly = False,
        select = True)
    Paq = fields.Char('Número de paquetes')
    serv_tipsa = fields.Many2one('servicio.tipsa', string="Tipo de servicio")
    #DATOS REMITENTE----------------------
    agencia_ori = fields.Char(string="Remitente")
    DirOri = fields.Char('Direccion')
    NumOri = fields.Char('Número de casa')
    PisOri = fields.Char('Número de piso')
    PobOri = fields.Char('Población')
    CPOri= fields.Char('Código postal')
    TlfOri = fields.Char('Telefono')
    CodProOri = fields.Char('Código provincial')
    CodOri = fields.Char('Código Destino')
    #DATOS DEL DESTINO ------------------------------
    NomDes = fields.Char('Destino', required =True)
    DirDes = fields.Char('Direccion')
    NumDes = fields.Char('Número de casa')
    PisDes = fields.Char('Número de piso')
    PobDes = fields.Char('Población')
    CPDes = fields.Char('Código postal')
    TlfDes = fields.Char('Telefono')
    CodProDes = fields.Char('Código provincial')
    CodDes = fields.Char('Código Destino')
    EmailDes = fields.Char('Email Destino')
    TipoViaDes = fields.Char('Tipo de vía del destinatario.', required =True)
    PersContacto = fields.Char('Persona de contacto')
    #------------------------------------------------
    #Datos etiqueta ---------------------------------
    formato = fields.Selection([('233','PDF'),
        ('226','TXT')],default="233")
    posicion_ini = fields.Char('Posicion inicial')
    peso = fields.Float('Peso')
    #------------------------------------------------
    #Descargar para etiqueta ------------------------
    file = fields.Binary('Layout')
    download_file = fields.Boolean('Descargar Archivo')
    cadena_decoding = fields.Text('Binario sin encoding')
    datas_fname = fields.Char('File Name', size=256)

    _defaults = {
        'download_file': False
    }

    @api.model
    def default_get(self,values):
        res = super(ws_etiqueta_fac,self).default_get(values)
        print ("...........------->>>>>",values)
        active_id = self._context.get('active_ids')
        account_id = self.env['account.invoice'].browse(active_id)
        partner = self.env['account.invoice'].browse(account_id.partner_id)
        user = self.env['account.invoice'].browse(account_id.user_id)
        objres = self.env['res.partner'].search([('id','=',partner.id.ids)])
        objres_remite = self.env['res.partner'].search([('id','=',user.id.ids)])
        print ("---------------->",user.id.ids)
        for account in account_id:
            res.update({
                'name_env': account.name,
                'NomDes':objres.name,
                'DirDes':objres.street,
                'NumDes':objres.num_home,
                'PisDes':objres.num_piso,
                'PobDes':objres.city,
                'CPDes':objres.zip,
                'TlfDes':objres.phone,
                'EmailDes':objres.email,
                'CodProDes':objres.codigo_provin,
                'TipoViaDes':objres.TipoVia,
                'PersContacto':objres.name,
                'agencia_ori':objres_remite.name,
                'DirOri':objres_remite.street,
                'NumOri':objres_remite.num_home,
                'PisOri':objres_remite.num_piso,
                'PobOri':objres_remite.city,
                'CPOri':objres_remite.zip,
                'TlfOri':objres_remite.phone,
                'CodProOri':objres_remite.codigo_provin,
                })
        print ("------------>",self.DirOri)
        return res





