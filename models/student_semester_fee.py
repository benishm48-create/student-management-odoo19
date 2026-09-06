# -*- coding: utf-8 -*-
from odoo import models, fields, api

GRADE_DISCOUNT_MAP = {
    'A+': 50.0,
    'A': 50.0,
    'B': 40.0,
    'C': 30.0,
    'D': 20.0,
    'E': 10.0,
    'F': 0.0,
}


class StudentSemesterFee(models.Model):
    _name = 'student.semester.fee'
    _description = 'Student Semester Fee Payment'
    _rec_name = 'semester_id'

    student_id = fields.Many2one('student.student', string='Student',
                                  required=True, ondelete='cascade')
    semester_id = fields.Many2one('student.semester', string='Semester', required=True)

    total_fee = fields.Float(related='semester_id.total_fee', string='Total Fee', readonly=True)

    discount_percent = fields.Float(string='Discount %', compute='_compute_discount', store=True)
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount', store=True)
    net_fee = fields.Float(string='Net Fee', compute='_compute_discount', store=True)

    paid_amount = fields.Float(string='Paid Amount')

    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Balance Due'),
        ('paid', 'Paid'),
    ], string='Status', compute='_compute_payment_status', store=True)

    @api.depends('total_fee', 'student_id.overall_grade')
    def _compute_discount(self):
        for record in self:
            grade = record.student_id.overall_grade
            pct = GRADE_DISCOUNT_MAP.get(grade, 0.0)
            record.discount_percent = pct
            record.discount_amount = record.total_fee * pct / 100.0
            record.net_fee = record.total_fee - record.discount_amount

    @api.depends('net_fee', 'paid_amount')
    def _compute_balance(self):
        for record in self:
            record.balance = record.net_fee - record.paid_amount

    @api.depends('paid_amount', 'net_fee')
    def _compute_payment_status(self):
        for record in self:
            if record.paid_amount <= 0:
                record.payment_status = 'unpaid'
            elif record.paid_amount >= record.net_fee and record.net_fee > 0:
                record.payment_status = 'paid'
            else:
                record.payment_status = 'partial'
