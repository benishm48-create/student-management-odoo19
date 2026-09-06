# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StudentMark(models.Model):
    _name = 'student.mark'
    _description = 'Student Subject Marks'
    _rec_name = 'subject_id'

    student_id = fields.Many2one('student.student', string='Student',
                                  required=True, ondelete='cascade')
    subject_id = fields.Many2one('student.subject', string='Subject', required=True)

    max_mark = fields.Float(string='Max Mark', default=100.0, required=True)
    obtained_mark = fields.Float(string='Obtained Mark')

    percentage = fields.Float(string='Percentage', compute='_compute_result', store=True)
    grade = fields.Char(string='Grade', compute='_compute_result', store=True)
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Result', compute='_compute_result', store=True)

    @api.depends('obtained_mark', 'max_mark')
    def _compute_result(self):
        for record in self:
            if record.max_mark > 0:
                pct = (record.obtained_mark / record.max_mark) * 100
            else:
                pct = 0.0
            record.percentage = pct

            if pct >= 90:
                record.grade = 'A+'
            elif pct >= 80:
                record.grade = 'A'
            elif pct >= 70:
                record.grade = 'B'
            elif pct >= 60:
                record.grade = 'C'
            elif pct >= 50:
                record.grade = 'D'
            elif pct >= 40:
                record.grade = 'E'
            else:
                record.grade = 'F'

            record.result = 'pass' if pct >= 40 else 'fail'

    @api.constrains('obtained_mark', 'max_mark')
    def _check_marks(self):
        for record in self:
            if record.obtained_mark < 0:
                raise ValidationError("Obtained Mark cannot be negative!")
            if record.obtained_mark > record.max_mark:
                raise ValidationError("Obtained Mark cannot be greater than Max Mark!")
