# -*- coding: utf-8 -*-
from odoo import models, fields


class FeeStructure(models.Model):
    _name = 'student.fee.structure'
    _description = 'Fee Structure'
    _order = 'fee_type asc'

    fee_type = fields.Char(string='Fee Type', required=True)
    amount = fields.Float(string='Amount', required=True)
