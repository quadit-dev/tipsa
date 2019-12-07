# -*- coding: utf-8 -*-
# Copyright 2019 QUADIT https://www.quadit.mx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models, _


class stock_picking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    state_env = fields.Selection([('draft', 'Sin envio'), ('posted', 'Envio')],
                                 string='Status', required=True, readonly=True,
                                 copy=False, default='draft')

    @api.multi
    def cambia_estado(self):
        estado = 'posted'
        self.update({
            'state_env': estado
        })
        return True
