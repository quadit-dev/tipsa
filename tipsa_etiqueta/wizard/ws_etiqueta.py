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
import logging

_logger = logging.getLogger(__name__)

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



class tipsa_servicio(models.Model):
    _name = 'tipsa.servicio'
    _inherit = 'tipsa.servicio'



class ws_etiqueta(models.Model):
    _name = 'ws.etiqueta'
    _description = 'Datos para etiqueta'
    opcion = fields.Many2one('tipsa.servicio',string="Opcion")
    name_env =fields.Char('Nombre envio')
    dtm_envio = fields.Datetime ('Fecha envio',
        readonly = False,
        select = True)
    agencia_ori = fields.Many2one('res.partner', string="Remitente")
    serv_tipsa = fields.Many2one('servicio.tipsa', string="Tipo de servicio")
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
    Paq = fields.Char('Número de paquetes')
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
        res = super(ws_etiqueta,self).default_get(values)
        active_id = self._context.get('active_ids')
        picking_id = self.env['stock.picking'].browse(active_id)
        partner = self.env['stock.picking'].browse(picking_id.partner_id)
        objres = self.env['res.partner'].search([('id','=',partner.id.ids)])
        for picking in picking_id:
            if picking.state_env == 'posted':
                raise ValidationError(_('[-] No se puede crear etiqueta. Envio y Etiqueta realizados'))
            res.update({
                'name_env': picking.name,
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
                'peso':picking.weight,
                'PersContacto':objres.name,
                'Paq':picking.number_of_packages,
                })
        return res


    @api.multi
    def genera_etiqueta(self,albaran):
        if self.formato == '233':
            form_c= 'PDF'
        else:
            form_c = 'TXT'
        url = self.opcion.url_login
        file = fields.Binary('Layout')
        headers = {'content-type': 'text/xml'}
        body =  """<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Body>
            <LoginWSService___LoginCli>
                <strCodAge>"""+str(self.opcion.agencia)+"""</strCodAge>
                <strCod>"""+str(self.opcion.user)+"""</strCod>
                <strPass>"""+str(self.opcion.password)+"""</strPass>
            </LoginWSService___LoginCli>
        </soap:Body>
        </soap:Envelope>"""
        response = requests.post(url,data=body,headers=headers)
        login = response.content
        ID = login[368:404]
        url_met = self.opcion.url_accion
        headers_met = {'content-type': 'text/xml'}
        body_met =  """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Header>
        <ROClientIDHeader xmlns="http://tempuri.org/">
            <ID>{"""+ID+"""}</ID>
        </ROClientIDHeader>
        </soap:Header>
        <soap:Body>
            <WebServService___ConsEtiquetaEnvio6>
                <strCodAgeOri>"""+self.opcion.agencia+"""</strCodAgeOri>
                <strAlbaran>"""+albaran+"""</strAlbaran>
                <intIdRepDet>"""+self.formato+"""</intIdRepDet>
                <strFormato>"""+form_c+"""</strFormato>
            </WebServService___ConsEtiquetaEnvio6>
        </soap:Body>
        </soap:Envelope>"""
        response_met = requests.post(url_met,data=body_met,headers=headers_met)
        metodo = response_met.content
        # parse an xml file by na
        myxml = fromstring(metodo)
        for element in myxml.iter():
            etiqueta = element.findtext('{http://tempuri.org/}strEtiqueta')
            if etiqueta:
                pdf = etiqueta
        final = base64.decodestring(pdf)

        return final

    @api.multi
    def genera_envio(self):
        url = self.opcion.url_login
        file = fields.Binary('Layout')
        headers = {'content-type': 'text/xml'}
        body =  """<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <soap:Body>
            <LoginWSService___LoginCli>
                <strCodAge>"""+self.opcion.agencia+"""</strCodAge>
                <strCod>"""+self.opcion.user+"""</strCod>
                <strPass>"""+self.opcion.password+"""</strPass>
            </LoginWSService___LoginCli>
        </soap:Body>
        </soap:Envelope>"""
        response = requests.post(url,data=body,headers=headers)
        login = response.content
        ID = login[368:404]
        pesoString = str(self.peso)
        split_envio = self.dtm_envio.split('-')
        split_envio_dia = split_envio[2].split(' ')
        date_envio = split_envio[0]+'/'+split_envio[1]+'/'+split_envio_dia[0]  # noqa
        url_met = self.opcion.url_accion
        headers_met = {'content-type': 'text/xml'}
        body_met =  """<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <soap:Header>
                        <ROClientIDHeader xmlnsopcion="http://tempuri.org/">
                            <ID>{"""+ID+"""}</ID>
                        </ROClientIDHeader>
                    </soap:Header>
                    <soap:Body>
                     <WebServService___GrabaEnvio18 xmlns="http://tempuri.org/">
                        <strCodAgeCargo>"""+str(self.opcion.agencia)+"""</strCodAgeCargo>
                        <strCodAgeOri>"""+str(self.opcion.agencia)+"""</strCodAgeOri>
                        <dtFecha>"""+date_envio+"""</dtFecha>
                        <strCodTipoServ>"""+str(self.serv_tipsa.codigo)+"""</strCodTipoServ>
                        <strCodCli>"""+str(self.opcion.agencia)+"""</strCodCli>
                        <strNomOri>"""+str(self.agencia_ori.name)+"""</strNomOri>
                        <strTipoViaOri>"""+str(self.agencia_ori.TipoVia)+"""</strTipoViaOri>
                        <strDirOri>"""+str(self.agencia_ori.street)+"""</strDirOri>
                        <strNumOri>"""+str(self.agencia_ori.num_home)+"""</strNumOri>
                        <strPisoOri>"""+str(self.agencia_ori.num_piso)+"""</strPisoOri>
                        <strPobOri>"""+str(self.agencia_ori.city)+"""</strPobOri>
                        <strCPOri>"""+str(self.agencia_ori.zip)+"""</strCPOri>
                        <strCodProOri>"""+str(self.agencia_ori.codigo_provin)+"""</strCodProOri>
                        <strTlfOri>"""+str(self.agencia_ori.phone)+"""</strTlfOri>
                        <strNomDes>"""+str(self.NomDes)+"""</strNomDes>
                        <strTipoViaDes>"""+str(self.TipoViaDes)+"""</strTipoViaDes>
                        <strDirDes>"""+str(self.DirDes)+"""</strDirDes>
                        <strNumDes>"""+str(self.NumDes)+"""</strNumDes>
                        <strPisoDes>"""+str(self.PisDes)+"""</strPisoDes>
                        <strPobDes>"""+str(self.PobDes)+"""</strPobDes>
                        <strCPDes>"""+str(self.CPDes)+"""</strCPDes>
                        <strCodProDes>"""+str(self.CodProDes)+"""</strCodProDes>
                        <strTlfDes>"""+str(self.TlfDes)+"""</strTlfDes>
                        <intPaq>"""+str(self.Paq)+"""</intPaq>
                        <dPesoOri>"""+pesoString+"""</dPesoOri>
                        <strPersContacto>"""+str(self.PersContacto)+"""</strPersContacto>
                        <boDesSMS>0</boDesSMS>
                        <boDesEmail>1</boDesEmail>
                        <strDesDirEmails>"""+str(self.EmailDes)+"""</strDesDirEmails>
                        <boInsert>1</boInsert>
                     </WebServService___GrabaEnvio18>
                    </soap:Body>
            </soap:Envelope>"""
        _logger.info("======> %r" % body_met)
        response_met = requests.post(url_met,data=body_met,headers=headers_met)
        metodo = response_met.content
        myxml = fromstring(metodo)
        for element in myxml.iter():
            etiqueta = element.findtext('{http://tempuri.org/}strAlbaranOut')
            if etiqueta:
                albaran = etiqueta
        return albaran



    @api.multi
    def genera_envio_etiqueta(self):
        albaran = self.genera_envio()
        pdf = self.genera_etiqueta(albaran)
        self.write({
                        'file': base64.b64encode(pdf),
                        'datas_fname': 'Etiqueta.pdf',
                        'download_file': True})
        active_id = self._context.get('active_ids')
        stock = self.env['stock.picking'].browse(active_id)
        stock_ids = stock.cambia_estado()
        env_tipsa = self.env['envio.tipsa']
        envio = env_tipsa.create({
                'name': self.name_env,
                'albaran': albaran,
                'agencia_ori': self.agencia_ori.name,
                'agencia_des': self.NomDes,
                'paq': self.Paq,
                'file': self.file,
                'datas_fname': self.datas_fname,
                'dtm_envio': self.dtm_envio,
                })


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ws.etiqueta',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',


        }





