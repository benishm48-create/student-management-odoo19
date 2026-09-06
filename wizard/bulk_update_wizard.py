# -*- coding: utf-8 -*-
from odoo import models, fields


class BulkUpdateWizard(models.TransientModel):
    _name = 'bulk.update.wizard'
    _description = 'Bulk Update Wizard'

    age = fields.Integer(string='New Age')
    department_id = fields.Many2one('student.department', string='New Department')

    def action_ok(self):
        # active_ids = list of student IDs selected (checked) in the list view
        student_ids = self.env.context.get('active_ids', [])
        students = self.env['student.student'].browse(student_ids)

        vals = {}
        if self.age:
            vals['age'] = self.age
        if self.department_id:
            vals['department_id'] = self.department_id.id

        if vals:
            students.write(vals)

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}