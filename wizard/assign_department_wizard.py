# -*- coding: utf-8 -*-
from odoo import models, fields


class AssignDepartmentWizard(models.TransientModel):
    _name = 'assign.department.wizard'
    _description = 'Assign Department Wizard'

    department_id = fields.Many2one(
        'student.department',
        string='Department',
        required=True
    )

    def action_assign(self):
        student_id = self.env.context.get('active_id')
        student = None

        if student_id:
            student = self.env['student.student'].browse(student_id)
            student.write({'department_id': self.department_id.id})

        # Only show the "under 5" warning if it's actually true
        if student and student.age < 5:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'This student is under 5 years old — please verify the age.',
                    'type': 'warning',
                    'sticky': True,
                },
            }

        # Otherwise, show the normal success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Department assigned successfully!',
                'type': 'success',
                'sticky': True,
            },
        }