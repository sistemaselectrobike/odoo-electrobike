# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
        if self.product_uom_qty < 0:
            self.product_uom_qty = 0
        return res

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        """
            complete override to just return result of _onchange_product_id_check_availability
        """
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        return self._onchange_product_id_check_availability()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:
                    message =  _('You plan to sell %s %s but you only have %s %s available in %s warehouse.') % \
                            (self.product_uom_qty, self.product_uom.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available accross all warehouses.') % \
                                (self.product_id.virtual_available, product.uom_id.name)

                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message' : message
                    }
                    return {'warning': warning_mess}
        return {}

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        if not self.product_uom or (self.product_id.uom_id.category_id.id != self.product_uom.category_id.id):
            self.product_uom = self.product_id.uom_id
        self._onchange_product_id_check_availability()

    def _check_routing(self):
        """ Verify the route of the product based on the warehouse
            return True if the product availibility in stock does not need to be verified,
            which is the case in MTO, Cross-Dock or Drop-Shipping
        """
        is_available = False
        product_routes = self.route_id or (self.product_id.route_ids + self.product_id.categ_id.total_route_ids)

        # Check MTO
        wh_mto_route = self.order_id.warehouse_id.mto_pull_id.route_id
        if wh_mto_route and wh_mto_route <= product_routes:
            is_available = True
        else:
            mto_route = False
            try:
                mto_route = self.env['stock.warehouse']._get_mto_route()
            except UserError:
                # if route MTO not found in ir_model_data, we treat the product as in MTS
                pass
            if mto_route and mto_route in product_routes:
                is_available = True
                