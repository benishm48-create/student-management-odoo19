# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Student(models.Model):
    _name = 'student.student'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Student Details'
    _order = 'name asc'

    name = fields.Char(string='Student Name', required=True , tracking = True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, tracking = True)
    department_id = fields.Many2one('student.department', string='Department', tracking =True)
    dob = fields.Date(string='Date of Birth', tracking = True)
    image = fields.Image(string='Photo', tracking = True)
    internal_notes = fields.Text(string="Internal Note", tracking = True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', tracking = True)

    subject_ids = fields.Many2many('student.subject', string='Subjects', tracking = True)

    teacher_id = fields.Many2one('student.teacher', string='Teacher', tracking = True)

    phone = fields.Char(string='Phone', tracking = True)
    email = fields.Char(string='Email', tracking = True)

    semester_fee_ids = fields.One2many('student.semester.fee', 'student_id', string='Semesters', tracking = True)
    mark_ids = fields.One2many('student.mark', 'student_id', string='Marks', tracking = True)

    overall_percentage = fields.Float(string='Overall Percentage',
                                       compute='_compute_overall_performance', store=True, tracking = True)
    overall_grade = fields.Char(string='Overall Grade',
                                 compute='_compute_overall_performance', store=True, tracking = True)

    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('graduated', 'Graduated'),
    ], string='Status', default='new', required=True, tracking = True)

    # New field: copied from Department's HOD via onchange
    hod_name = fields.Char(string='Head of Department', tracking = True)

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

    @api.depends('mark_ids.percentage')
    def _compute_overall_performance(self):
        for record in self:
            marks = record.mark_ids
            avg = sum(marks.mapped('percentage')) / len(marks) if marks else 0.0
            record.overall_percentage = avg

            if not marks:
                record.overall_grade = ''
            elif avg >= 90:
                record.overall_grade = 'A+'
            elif avg >= 80:
                record.overall_grade = 'A'
            elif avg >= 70:
                record.overall_grade = 'B'
            elif avg >= 60:
                record.overall_grade = 'C'
            elif avg >= 50:
                record.overall_grade = 'D'
            elif avg >= 40:
                record.overall_grade = 'E'
            else:
                record.overall_grade = 'F'

    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if record.dob and record.dob > date.today():
                raise ValidationError("Date of Birth cannot be in the future!")
            if record.age and record.age > 100:
                raise ValidationError("Age seems invalid. Please check the Date of Birth.")

    @api.onchange('dob')
    def _onchange_dob(self):
        if self.dob and self.dob > date.today():
            return {
                'warning': {
                    'title': 'Invalid Date',
                    'message': 'Date of Birth cannot be in the future!',
                }
            }

    # New: passes hod_name from Department to Student when department is picked
    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.hod_name = self.department_id.hod_name
        else:
            self.hod_name = False

    @api.model
    def get_total_student_count(self):
        return self.search_count([])

    @api.model
    def get_students_by_department(self, department_id):
        return self.search([('department_id', '=', department_id)])

    @api.model
    def count_confirmed_students(self):
        return self.search_count([('state', '=', 'confirmed')])

    @api.model
    def get_all_male_names(self):
        students = self.search([('gender', '=', 'male')])
        return students.mapped('name')

    @api.model
    def get_students_sorted_by_age(self):
        students = self.search([])
        return students.sorted(key=lambda s: s.age)

    def get_older_students(self):
        return self.filtered(lambda s: s.age > 18)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_graduate(self):
        self.write({'state': 'graduated'})

    def action_reset_new(self):
        self.write({'state': 'new'})