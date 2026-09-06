from odoo import models, fields


class ProductMake(models.Model):
    _name = 'product.make'
    _description = 'Product Make'
    _order = 'name'

    name = fields.Char(
        string='Make Name',
        required=True,
    )

    category_ids = fields.Many2many(
        'product.category',
        'product_make_category_rel',
        'make_id',
        'category_id',
        string='Categories',
    )