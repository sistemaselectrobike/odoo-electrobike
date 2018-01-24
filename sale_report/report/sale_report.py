# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools

class PosSaleReport_EB(models.Model):
    _name = "report.all.channels.sales.eb"
    _description = "Reporte general de ventas"
    _auto = False

    name = fields.Char('Orden de venta', readonly=True)
    puntodeventa = fields.Char('Punto de venta', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', readonly=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Producto (Template)', readonly=True)
    date_order = fields.Datetime(string='Fecha de la orden', readonly=True)
    user_id = fields.Many2one('res.users', 'Vendedor', readonly=True)
    categ_id = fields.Many2one('product.category', 'Categoría de producto', readonly=True)
    company_id = fields.Many2one('res.company', 'Companía', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Lista de precios', readonly=True)
    country_id = fields.Many2one('res.country', 'País del cliente', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica', readonly=True)
    team_id = fields.Many2one('crm.team', 'Canal de ventas', readonly=True)
    product_qty = fields.Float('Cantidad', readonly=True)
    price_subtotal = fields.Float(string='Subtotal sin IVA', readonly=True)
    price_total = fields.Float('Total con IVA', readonly=True)

    def _so(self):
        so_str = """
            WITH currency_rate as (%s)
                SELECT sol.id AS id,
                    so.name AS name,
                    'Ventas Corp' AS puntodeventa,
                    so.partner_id AS partner_id,
                    sol.product_id AS product_id,
                    pro.product_tmpl_id AS product_tmpl_id,
                    so.date_order AS date_order,
                    so.user_id AS user_id,
                    pt.categ_id AS categ_id,
                    so.company_id AS company_id,
                    sol.price_total / COALESCE(cr.rate, 1.0) AS price_total,
                    so.pricelist_id AS pricelist_id,
                    rp.country_id AS country_id,
                    sol.price_subtotal / COALESCE (cr.rate, 1.0) AS price_subtotal,
                    (sol.product_uom_qty / u.factor * u2.factor) as product_qty,
                    so.analytic_account_id AS analytic_account_id,
                    so.team_id AS team_id

            FROM sale_order_line sol
                    JOIN sale_order so ON (sol.order_id = so.id)
                    LEFT JOIN product_product pro ON (sol.product_id = pro.id)
                    JOIN res_partner rp ON (so.partner_id = rp.id)
                    LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                    LEFT JOIN product_pricelist pp ON (so.pricelist_id = pp.id)
                    LEFT JOIN currency_rate cr ON (cr.currency_id = pp.currency_id AND
                        cr.company_id = so.company_id AND
                        cr.date_start <= COALESCE(so.date_order, now()) AND
                        (cr.date_end IS NULL OR cr.date_end > COALESCE(so.date_order, now())))
                    LEFT JOIN product_uom u on (u.id=sol.product_uom)
                    LEFT JOIN product_uom u2 on (u2.id=pt.uom_id)
        """ % self.env['res.currency']._select_companies_rates()
        return so_str

    def _pos(self):
        pos_str = """
                 SELECT
                    (-1) * pol.id AS id,
                    pos.name AS name,
                    config.name AS puntodeventa,
                    pos.partner_id AS partner_id,
                    pol.product_id AS product_id,
                    pro.product_tmpl_id AS product_tmpl_id,
                    pos.date_order AS date_order,
                    pos.user_id AS user_id,
                    pt.categ_id AS categ_id,
                    pos.company_id AS company_id,
                    ((pol.qty * pol.price_unit) * (100 - pol.discount) / 100) AS price_total,
                    pos.pricelist_id AS pricelist_id,
                    rp.country_id AS country_id,
                    ((pol.qty * pol.price_unit) * (100 - pol.discount) / 100)*1.16 AS price_total,
                    (pol.qty * u.factor) AS product_qty,
                    NULL AS analytic_account_id,
                    config.crm_team_id AS team_id

                FROM pos_order_line AS pol
                    JOIN pos_order pos ON (pos.id = pol.order_id)
                    LEFT JOIN pos_session session ON (session.id = pos.session_id)
                    LEFT JOIN pos_config config ON (config.id = session.config_id)
                    LEFT JOIN product_product pro ON (pol.product_id = pro.id)
                    LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                    LEFT JOIN product_category AS pc ON (pt.categ_id = pc.id)
                    LEFT JOIN res_company AS rc ON (pos.company_id = rc.id)
                    LEFT JOIN res_partner rp ON (rc.partner_id = rp.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
         """
        return pos_str

    def _from(self):
        return """(%s UNION ALL %s)""" % (self._so(), self._pos())

    def get_main_request(self):
        request = """
            CREATE or REPLACE VIEW %s AS
                SELECT id AS id,
                    name,
                    puntodeventa,
                    partner_id,
                    product_id,
                    product_tmpl_id,
                    date_order,
                    user_id,
                    categ_id,
                    company_id,
                    price_total,
                    pricelist_id,
                    analytic_account_id,
                    country_id,
                    team_id,
                    price_subtotal,
                    product_qty
                FROM %s
                AS foo""" % (self._table, self._from())
        return request

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(self.get_main_request())