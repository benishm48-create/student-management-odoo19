# -*- coding: utf-8 -*-
from odoo import models, fields


class Department(models.Model):
    _name = 'student.department'
    _description = 'Student Department'
    _order = 'name asc'

    name = fields.Char(string='Department Name', required=True)

    # New field: Head of Department
    hod_name = fields.Char(string='Head of Department')

    student_ids = fields.One2many(
        'student.student',
        'department_id',
        string='Students'
    )