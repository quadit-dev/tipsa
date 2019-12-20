# -*- coding: utf-8 -*-
# Copyright 2019 QUADIT https://www.quadit.mx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

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

    def obtener_servicio(self):
        tipsa = self.env['tipsa.servicio']
        tipsa_id = tipsa.search([('id', '=', '1')])
        return tipsa_id

    def obtener_remitente(self):
        res = self.env['res.partner']
        res_partner = res.search([('name', '=', 'Soluziono desarrollos editoriales SL')])
        return res_partner

    def obtener_tipo(self):
        servicio = self.env['servicio.tipsa']
        servicio_tipo = servicio.search([('name', '=', '14 HORAS')])
        return servicio_tipo

    opcion = fields.Many2one('tipsa.servicio', string="Opcion",default=obtener_servicio)
    name_env = fields.Char('Nombre envio')
    dtm_envio = fields.Datetime('Fecha de envío',
                                readonly=False,
                                select=True,
                                default=lambda self: fields.datetime.now())
    agencia_ori = fields.Many2one('res.partner', string="Remitente",default=obtener_remitente)
    serv_tipsa = fields.Many2one('servicio.tipsa', string="Tipo de servicio",default=obtener_tipo)
    # DATOS DEL DESTINO ------------------------------
    NomDes = fields.Char('Destino', required=True)
    DirDes = fields.Char('Direccion',required=True)
    NumDes = fields.Char('Número de casa')
    PisDes = fields.Char('Número de piso')
    PobDes = fields.Char('Población',required=True)
    CPDes = fields.Char('Código postal',required=True)
    TlfDes = fields.Char('Telefono',required=True)
    CodProDes = fields.Char('Código provincial',required=True)
    CodDes = fields.Char('Código Destino',required=True)
    EmailDes = fields.Char('Email Destino',required=True)
    TipoViaDes = fields.Selection([
        ('C', 'Calle'),
        ('PZA', 'Plaza'),
        ('AV', 'Avenida')],
        string='Tipo de vía',default ='C',required=True)
    Paq = fields.Char('Número de paquetes')
    PersContacto = fields.Char('Persona de contacto')
    # ------------------------------------------------
    # Datos etiqueta ---------------------------------
    formato = fields.Selection([('233', 'PDF'),
                                ('226', 'TXT')], default="233")
    posicion_ini = fields.Char('Posicion inicial')
    peso = fields.Float('Peso')
    # ------------------------------------------------
    # Descargar para etiqueta ------------------------
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
        suma_peso = 0
        suma_paq = 0
        
        for picking in picking_id:
            partner = self.env['stock.picking'].browse(picking.partner_id.ids)
            objres = self.env['res.partner'].search([('id','=',partner.id)])
            suma_peso= suma_peso + picking.weight
            suma_paq = suma_paq + picking.number_of_packages
            cod = objres.zip
            if picking.state_env == 'posted':
                raise ValidationError(
                    _('[-] No se puede crear etiqueta. Envio y Etiqueta realizados'))
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
            'CodProDes':cod,
            'PersContacto':objres.name,
            'Paq':suma_paq,
            })

        return res

    @api.multi
    def genera_etiqueta(self, albaran):
        if self.formato == '233':
            form_c = 'PDF'
        else:
            form_c = 'TXT'
        url = self.opcion.url_login
        file = fields.Binary('Layout')
        headers = {'content-type': 'text/xml'}
        body = """<?xml version="1.0" encoding="UTF-8"?>
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
        response = requests.post(url, data=body, headers=headers)
        login = response.content
        ID = login[368:404]
        url_met = self.opcion.url_accion
        headers_met = {'content-type': 'text/xml'}
        body_met = """<?xml version="1.0" encoding="utf-8"?>
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
        response_met = requests.post(url_met, data=body_met, headers=headers_met)
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
        body = """<?xml version="1.0" encoding="utf-8"?>
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
        response = requests.post(url, data=body, headers=headers)
        login = response.content
        _logger.info("======> %r" % body)
        _logger.info("======> %r" % login)
        ID = login[368:404]
        pesoString = str(self.peso)
        split_envio = self.dtm_envio.split('-')
        split_envio_dia = split_envio[2].split(' ')
        date_envio = split_envio[0]+'/'+split_envio[1]+'/'+split_envio_dia[0]  # noqa
        url_met = self.opcion.url_accion
        headers_met = {'content-type': 'text/xml'}
        body_met = """<?xml version="1.0" encoding="utf-8"?>
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
                        <strCodAgeCargo>"""+str(self.opcion.agencia)+"""</strCodAgeCargo>
                        <strCodAgeOri>"""+str(self.opcion.agencia)+"""</strCodAgeOri>
                        <dtFecha>"""+date_envio+"""</dtFecha>
                        <strCodTipoServ>"""+str(self.serv_tipsa.codigo)+"""</strCodTipoServ>
                        <strCodCli>"""+str(self.opcion.user)+"""</strCodCli>
                        <strNomOri>"""+str(self.agencia_ori.name)+"""</strNomOri>
                        <strTipoViaOri>"""+str(self.TipoViaDes)+"""</strTipoViaOri>
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
        response_met = requests.post(url_met, data=body_met, headers=headers_met)
        metodo = response_met.content
        myxml = fromstring(metodo)
        for element in myxml.iter():
            etiqueta = element.findtext('{http://tempuri.org/}strAlbaranOut')
            if etiqueta:
                albaran = etiqueta
        return albaran

    @api.multi
    def genera_envio_etiqueta(self):
        albaran = " "
        albaran = self.genera_envio()
        pdf = self.genera_etiqueta(albaran)
        self.write({
            'file': base64.b64encode(pdf),
            'datas_fname': 'Etiqueta.pdf',
            'download_file': True})
        cad = " "
        active_id = self._context.get('active_ids')
        stock = self.env['stock.picking'].browse(active_id)
        for picking in stock:
            cad = cad + picking.name + "\n"
            stock_ids = picking.cambia_estado()
        env_tipsa = self.env['envio.tipsa']
        envio = env_tipsa.create({
            'name': self.name_env,
            'albaran': albaran,
            'agencia_ori': self.agencia_ori.name,
            'agencia_des': self.NomDes,
            'paq': self.Paq,
            'file': self.file,
            'datas_fname': self.datas_fname,
            'albaran_soluziono':cad,
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

