# -*- coding: utf-8 -*-

from lxml import etree
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        res['context']['apply_extra_domain'] = self.location_id.usage != 'supplier'
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockMoveLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        # BAD fixed to apply domain based on the context
        if self._context.get('apply_extra_domain') and view_type == 'tree':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='lot_id']"):
                node.set('domain', "[('product_id', '=', parent.product_id), ('quant_ids.location_id', 'child_of', location_id)]")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
