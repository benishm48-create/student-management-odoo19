# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Semester(models.Model):
    _name = 'student.semester'
    _description = 'Semester'
    _order = 'name asc'

    name = fields.Selection([
        ('sem1', 'Semester 1'),
        ('sem2', 'Semester 2'),
        ('sem3', 'Semester 3'),
        ('sem4', 'Semester 4'),
        ('sem5', 'Semester 5'),
        ('sem6', 'Semester 6'),
    ], string='Semester', required=True)

    fee_ids = fields.Many2many(
        'student.fee.structure',
        string='Fees'
    )

    total_fee = fields.Float(
        string='Total Fees',
        compute='_compute_total_fee',
        store=True
    )

    @api.depends('fee_ids.amount')
    def _compute_total_fee(self):
        for record in self:
            record.total_fee = sum(record.fee_ids.mapped('amount'))
