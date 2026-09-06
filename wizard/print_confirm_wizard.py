# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StudentPrintConfirmWizard(models.TransientModel):
    _name = 'student.print.confirm.wizard'
    _description = 'Confirm Print Student Details'

    student_id = fields.Many2one('student.student', string='Student', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        student_id = self.env.context.get('active_id')
        if student_id:
            res['student_id'] = student_id
        return res

    def action_confirm_print(self):
        self.ensure_one()
        return self.env.ref('students_management.action_report_student').report_action(self.student_id)
