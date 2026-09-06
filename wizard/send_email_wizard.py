# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SendEmailWizard(models.TransientModel):
    _name = 'student.send.email.wizard'
    _description = 'Send Email to Student'

    student_id = fields.Many2one('student.student', string='Student')
    recipient_email = fields.Char(string='To', required=True)
    subject = fields.Char(string='Subject', required=True)
    body = fields.Html(string='Message')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        student_id = self.env.context.get('active_id')
        if student_id:
            student = self.env['student.student'].browse(student_id)
            res['student_id'] = student.id
            res['recipient_email'] = student.email
            res['subject'] = 'Regarding your enrollment - %s' % (student.name or '')
        return res

    def action_send(self):
        for wizard in self:
            self.env['mail.mail'].create({
                'subject': wizard.subject,
                'body_html': wizard.body or '',
                'email_to': wizard.recipient_email,
            }).send()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sent',
                'message': 'Email has been sent successfully!',
                'type': 'success',
                'sticky': False,
            },
        }
