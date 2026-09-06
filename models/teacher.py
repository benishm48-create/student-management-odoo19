# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Teacher(models.Model):
    _name = 'student.teacher'
    _description = 'Teacher Details'
    _order = 'name asc'

    name = fields.Char(string='Teacher Name', required=True)
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    image = fields.Image(string='Photo')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')

    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    department_id = fields.Many2one('student.department', string='Department')
    subject_ids = fields.Many2many('student.subject', string='Subjects Taught')

    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', required=True)

    # Students assigned to this teacher (inverse of student.teacher_id)
    student_ids = fields.One2many('student.student', 'teacher_id', string='Students')
    student_count = fields.Integer(string='Student Count', compute='_compute_student_count')

    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = date.today()
                record.age = today.year - record.dob.year - (
                    (today.month, today.day) < (record.dob.month, record.dob.day)
                )
            else:
                record.age = 0

    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if record.dob and record.dob > date.today():
                raise ValidationError("Date of Birth cannot be in the future!")

    def action_set_active(self):
        self.write({'state': 'active'})

    def action_set_inactive(self):
        self.write({'state': 'inactive'})
