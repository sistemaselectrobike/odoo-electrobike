# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """
            Check availability of the quantity before final confrimation of sale order
            to make sure that, sale order can be confirm which have enough quantity to feed
        """
        if any(not l.is_available for l in self.mapped('order_line')):
            raise UserError(_('Some of your products in order does not have enough quantity available'))
        res = super(SaleOrder, self).action_confirm()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_available = fields.Boolean(compute='_check_qty_availability')

    @api.multi
    def _check_qty_availability(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            line.is_available = True
            if line.product_id.type == 'product' and line.state in ['draft', 'sent']:
                product = line.product_id.with_context(warehouse=line.order_id.warehouse_id.id)
                product_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                    is_available = line._check_routing()
                    if not is_available:
                        line.is_available = False

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        """
            Inherited to set the available qty as ordered qty when order qty not enough on stock
        """
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if res.get('warning'):
            product = self.product_id.with_context(warehouse=self.order_id.warehouse_id.id)
            self.product_uom_qty = product.virtual_available
        return res

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        """
            complete override to just return result of _onchange_product_id_check_availability
        """
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        return self._onchange_product_id_check_availability()
