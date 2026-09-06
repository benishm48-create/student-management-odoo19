# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    product_tmpl_ids = fields.One2many(
        'product.template', 'categ_id',
        string='Products in Category'
    )

    has_products = fields.Boolean(
        string='Has Products',
        compute='_compute_has_products',
        store=True
    )

    @api.depends('product_tmpl_ids')
    def _compute_has_products(self):
        for categ in self:
            categ.has_products = bool(categ.product_tmpl_ids)
