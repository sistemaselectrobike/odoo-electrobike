from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    
    _inherit = 'account.invoice.report'
    
    standard_price = fields.Float(string='Costo', readonly=True)
    extended_standard_price = fields.Float(string="Costo extendido", readonly=True)
    discount = fields.Char(string="Descuento", readonly=True)
    discount_amount = fields.Float(string="Monto de descuento", readonly=True)
    
    def _select(self):
        select_str = """
            SELECT sub.id, sub.discount, sub.date, sub.standard_price, sub.standard_price*sub.product_qty as extended_standard_price, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                sub.product_qty, sub.price_total as price_total, sub.price_average as price_average,
                COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id, 
                (sub.price_unit * sub.product_qty) - sub.price_total as discount_amount
        """
        return select_str
        
    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id, ail.discount::text||'%' as discount,
                    ai.date_invoice AS date, (select value_float from ir_property where res_id = 'product.product,'||ail.product_id::text and name = 'standard_price' limit 1) as standard_price,
                    ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
                    1 AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id,
                    sum(ail.price_unit * invoice_type.sign) as price_unit,
                    coalesce(SUM ((invoice_type.sign_qty * ail.quantity) / u.factor * u2.factor),sum(invoice_type.sign_qty * ail.quantity)) AS product_qty,
                    SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) * invoice_type.sign AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY ail.id, ail.discount::text||'%', ail.product_id, ail.account_analytic_id, ai.date_invoice, ai.id,
                    ai.partner_id, ai.payment_term_id, u2.name, u2.id, ai.currency_id, ai.journal_id,
                    ai.fiscal_position_id, ai.user_id, ai.company_id, ai.type, invoice_type.sign, ai.state, pt.categ_id,
                    ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual_company_signed,
                    ai.amount_total_company_signed, ai.commercial_partner_id, partner.country_id
        """
        return group_by_str
