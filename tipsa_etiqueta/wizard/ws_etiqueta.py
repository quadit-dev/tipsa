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
from xml.etree.ElementTree import XML, fromstring, tostring, parse


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
    dtm_envio = fields.Datetime ('Fecha envio',
        readonly = False,
        select = True)
    agencia_ori = fields.Many2one('res.partner', string="Agencia Origen")
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
    bulto_desde = fields.Char('Bulto desde')
    bulto_hasta = fields.Char('Bulto hasta')
    posicion_ini = fields.Char('Posicion inicial')
    #------------------------------------------------
    #Descargar para etiqueta ------------------------
    file = fields.Binary('Layout')
    download_file = fields.Boolean('Descargar Archivo')
    cadena_decoding = fields.Text('Binario sin encoding')
    datas_fname = fields.Char('File Name', size=256)

    _defaults = {
        'download_file': False,
        'type': 'pdf',
    }

    @api.model
    def default_get(self,values):
        print("########## VALUES ", values)
        res = super(ws_etiqueta,self).default_get(values)
        active_id = self._context.get('active_ids')
        picking_id = self.env['stock.picking'].browse(active_id)
        partner = self.env['stock.picking'].browse(picking_id.partner_id)
        objres = self.env['res.partner'].search([('id','=',partner.id.ids)])
        for picking in picking_id:
            res.update({
                'NomDes':objres.name,
                'CodDes':objres.codigo_tipsa,
                'DirDes':objres.street,
                'NumDes':objres.num_home,
                'PisDes':objres.num_piso,
                'PobDes':objres.city,
                'CPDes':objres.zip,
                'TlfDes':objres.phone,
                'EmailDes':objres.email,
                'CodProDes':objres.codigo_provin
                })
        return res


    @api.multi
    def genera_etiqueta(self,albaran):
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
        print login
        print ("---------------------->",ID)
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
                <intIdRepDet>233</intIdRepDet>
                <strFormato>PDF</strFormato>
            </WebServService___ConsEtiquetaEnvio6>
        </soap:Body>
        </soap:Envelope>"""
        response_met = requests.post(url_met,data=body_met,headers=headers_met)
        metodo = response_met.content
        print ("---------------->",ID)
        print ("---------------->",metodo)
        # parse an xml file by na
        myxml = fromstring(metodo)
        for element in myxml.iter():
            etiqueta = element.findtext('{http://tempuri.org/}strEtiqueta')
            if etiqueta:
                pdf = etiqueta
        final = base64.decodestring(pdf)
        print final
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
        print login
        print ("---------------------->",self.dtm_envio)
         #split de fecha creacion
        split_envio = self.dtm_envio.split('-')
        split_envio_dia = split_envio[2].split(' ')
        date_envio = split_envio[0]+'/'+split_envio[1]+'/'+split_envio_dia[0]  # noqa
        url_met = self.opcion.url_accion
        print ("---------------------->",date_envio)
        headers_met = {'content-type': 'text/xml'}
        body_met =  """<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <soap:Header>
                        <ROClientIDHeader xmlns="http://tempuri.org/">
                            <ID>{"""+ID+"""}</ID>
                        </ROClientIDHeader>
                    </soap:Header>
                    <soap:Body>
                     <WebServService___GrabaEnvio18 xmlns="http://tempuri.org/">
                        <strCodAgeCargo>"""+self.agencia_ori.codigo_tipsa+"""</strCodAgeCargo>
                        <strCodAgeOri>"""+self.agencia_ori.codigo_tipsa+"""</strCodAgeOri>
                        <dtFecha>"""+date_envio+"""</dtFecha>
                        <strCodAgeDes>000000</strCodAgeDes>
                        <strCodTipoServ>14</strCodTipoServ>
                        <strCodCli>33333</strCodCli>
                        <strCodCliDep>33333</strCodCliDep>
                        <strNomOri>"""+self.agencia_ori.name+"""</strNomOri>
                        <strDirOri>"""+self.agencia_ori.street+"""</strDirOri>
                        <strNumOri>"""+self.agencia_ori.num_home+"""</strNumOri>
                        <strPisoOri>"""+self.agencia_ori.num_piso+"""</strPisoOri>
                        <strPobOri>"""+self.agencia_ori.city+"""</strPobOri>
                        <strCPOri>"""+self.agencia_ori.zip+"""</strCPOri>
                        <strCodProOri>"""+self.agencia_ori.codigo_provin+"""</strCodProOri>
                        <strTlfOri>"""+self.agencia_ori.phone+"""</strTlfOri>
                        <strNomDes>"""+self.NomDes+"""</strNomDes>
                        <strDirDes>"""+self.DirDes+"""</strDirDes>
                        <strNumDes>"""+self.NumDes+"""</strNumDes>
                        <strPisoDes>"""+self.PisDes+"""</strPisoDes>
                        <strPobDes>"""+self.PobDes+"""</strPobDes>
                        <strCPDes>"""+self.CPDes+"""</strCPDes>
                        <strCodProDes>"""+self.CodProDes+"""</strCodProDes>
                        <strTlfDes>"""+self.TlfDes+"""</strTlfDes>
                        <intPaq>"""+self.Paq+"""</intPaq>
                        <strPersContacto>"""+self.PersContacto+"""</strPersContacto>
                        <boDesSMS>0</boDesSMS>
                        <boDesEmail>1</boDesEmail>
                        <strDesDirEmails>"""+self.EmailDes+"""</strDesDirEmails>
                        <boInsert>1</boInsert>
                     </WebServService___GrabaEnvio18>
                    </soap:Body>
            </soap:Envelope>"""
        print body_met
        response_met = requests.post(url_met,data=body_met,headers=headers_met)
        metodo = response_met.content
        print ("---------------->",ID)
        print ("---------------->",metodo)
        # parse an xml file by na
        myxml = fromstring(metodo)
        list = []
        for element in myxml.iter():
            etiqueta = element.findtext('{http://tempuri.org/}strAlbaranOut')
            if etiqueta:
                albaran = etiqueta
                print albaran
            print element

        print myxml

        return albaran


    @api.multi
    def genera_envio_etiqueta(self):
        albaran = self.genera_envio()
        pdf = self.genera_etiqueta(albaran)
        self.write({
                        'file': base64.b64encode(pdf),
                        'datas_fname': 'Etiqueta.pdf',
                        'download_file': True})
        print "HOLA"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ws.etiqueta',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }





