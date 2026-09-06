from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_category_id = fields.Many2one(
        'product.category',
        string='Category',
    )