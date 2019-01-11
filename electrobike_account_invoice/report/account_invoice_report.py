from odoo import tools
from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    
    _inherit = 'account.invoice.report'
    
    standard_price = fields.Float(string='Costo', readonly=True)
    extended_standard_price = fields.Float(string="Costo extendido", readonly=True)
    discount = fields.Char(string="Descuento", readonly=True)
    discount_amount = fields.Float(string="Monto de descuento", readonly=True)
    product_net_qty = fields.Float(string="Cantidad neta", readonly=True)
    
    def _select(self):
        return super(AccountInvoiceReport,self)._select()+",sub.product_net_qty, sub.discount,sub.standard_price,sub.standard_price*sub.product_net_qty as extended_standard_price,(sub.price_unit * sub.product_net_qty) - sub.price_total as discount_amount"
        
    def _sub_select(self):
        return super(AccountInvoiceReport,self)._sub_select()+",ail.discount::text||'%' as discount,(select value_float from ir_property where res_id = 'product.product,'||ail.product_id::text and name = 'standard_price' limit 1) as standard_price,sum(ail.price_unit * invoice_type.sign) as price_unit,coalesce(SUM ((invoice_type.sign_qty * ail.quantity) / u.factor * u2.factor),sum(invoice_type.sign_qty * ail.quantity)) AS product_net_qty"
       
    def _group_by(self):
        return super(AccountInvoiceReport,self)._group_by()+",ail.discount::text||'%'"
