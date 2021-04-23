# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.model
    @api.returns('stock.location.route', lambda value: value.id)
    def _get_mto_route(self):
        mto_route = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)
        if not mto_route:
            mto_route = self.env['stock.location.route'].search([('name', 'like', _('Make To Order'))], limit=1)
        if not mto_route:
            raise UserError(_('Can\'t find any generic Make To Order route.'))
        return mto_route
