# -*- coding: utf-8 -*-
from odoo import models, fields


class Subject(models.Model):
    _name = 'student.subject'
    _description = 'Subject'
    _order = 'name asc'

    name = fields.Char(string='Subject Name', required=True)