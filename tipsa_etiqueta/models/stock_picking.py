# -*- coding: utf-8 -*-
from openerp import _, api, fields, models

class stock_picking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    state_env = fields.Selection([('draft', 'Sin envio'), ('posted', 'Envio')],
        string='Status',required=True, readonly=True,
        copy=False,default='draft')




    @api.multi
    def cambia_estado(self):
        estado = 'posted'
        self.update({
            'state_env':estado
            })
        return True
