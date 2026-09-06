# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class TeacherLeave(models.Model):
    _name = 'teacher.leave'
    _description = 'Teacher Leave'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'leave_from desc'

    # =========================================================
    # BASIC INFORMATION
    # =========================================================

    name = fields.Char(
        string='Leave Reference',
        required=True,
        readonly=True,
        default='New',
        copy=False,
        tracking=True,
    )

    teacher_id = fields.Many2one(
        'student.teacher',
        string='Teacher',
        required=True,
        tracking=True,
    )

    department_id = fields.Many2one(
        'student.department',
        string='Department',
        tracking=True,
    )

    subject_ids = fields.Many2many(
        'student.subject',
        string='Subjects',
        tracking=True,
    )

    student_ids = fields.Many2many(
        'student.student',
        string='Students',
        tracking=True,
    )

    # =========================================================
    # LEAVE INFORMATION
    # =========================================================

    leave_from = fields.Date(
        string='Leave From',
        required=True,
        tracking=True,
    )

    leave_to = fields.Date(
        string='Leave To',
        required=True,
        tracking=True,
    )

    reason = fields.Text(
        string='Leave Reason',
        required=True,
        tracking=True,
    )

    substitute_teacher_id = fields.Many2one(
        'student.teacher',
        string='Substitute Teacher',
        tracking=True,
    )

    # =========================================================
    # STATUS
    # =========================================================

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Pending Approval'),
            ('approved', 'Approved'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True,
    )

    approved_date = fields.Datetime(
        string='Approved Date',
        readonly=True,
        tracking=True,
    )

    # =========================================================
    # CREATE
    # =========================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get('name', 'New') == 'New':

                vals['name'] = (
                    self.env['ir.sequence'].next_by_code(
                        'teacher.leave'
                    )
                    or 'New'
                )

        records = super().create(vals_list)

        for record in records:

            record.message_post(
                body='Teacher Leave request created.',
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

        return records

    # =========================================================
    # ONCHANGE TEACHER
    # =========================================================

    @api.onchange('teacher_id')
    def _onchange_teacher_id(self):

        if not self.teacher_id:

            self.department_id = False
            self.subject_ids = [(5, 0, 0)]
            self.student_ids = [(5, 0, 0)]

            return

        self.department_id = self.teacher_id.department_id

        self.subject_ids = self.teacher_id.subject_ids

        # Only this teacher's students
        self.student_ids = self.env['student.student'].search([
            ('teacher_id', '=', self.teacher_id.id)
        ])

    # =========================================================
    # TEACHER SUBMIT
    #
    # DRAFT -> PENDING APPROVAL
    #
    # NO EMAIL HERE
    # NO APPROVAL HERE
    # =========================================================

    def action_submit(self):

        for record in self:

            if not record.teacher_id:
                raise UserError(
                    'Please select a teacher.'
                )

            if not record.leave_from:
                raise UserError(
                    'Please select Leave From date.'
                )

            if not record.leave_to:
                raise UserError(
                    'Please select Leave To date.'
                )

            if record.leave_to < record.leave_from:
                raise UserError(
                    'Leave To date cannot be before Leave From date.'
                )

            if not record.reason:
                raise UserError(
                    'Please enter the leave reason.'
                )

            if not record.substitute_teacher_id:
                raise UserError(
                    'Please select a Substitute Teacher before '
                    'submitting the leave request.'
                )

            # Make sure students belong to this teacher
            record.student_ids = self.env[
                'student.student'
            ].search([
                ('teacher_id', '=', record.teacher_id.id)
            ])

            # ONLY change state
            record.write({
                'state': 'submitted',
            })

            record.message_post(
                body=(
                    '<b>Leave Request Submitted</b><br/>'
                    f'Teacher: <b>{record.teacher_id.name}</b><br/>'
                    'Status: <b>Pending HOD Approval</b><br/><br/>'
                    'Student email has <b>NOT</b> been sent yet.'
                ),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

    # =========================================================
    # HOD / ADMIN APPROVE
    #
    # PENDING APPROVAL -> APPROVED
    #
    # EMAIL SENT ONLY AFTER APPROVAL
    # =========================================================

    def action_approve(self):

        # HOD or Odoo Administrator can approve.
        is_hod = self.env.user.has_group(
            'students_management.group_student_hod'
        )
        is_admin = self.env.user.has_group('base.group_system')

        if not (is_hod or is_admin):
            raise UserError(
                'Only the HOD or Administrator can approve '
                'teacher leave requests.'
            )

        for record in self:

            if record.state != 'submitted':
                raise UserError(
                    'Only Pending Approval leave requests '
                    'can be approved.'
                )

            # =================================================
            # 1. APPROVE FIRST
            # =================================================
            # This is intentionally done BEFORE sending email.
            # Therefore the email template sees the leave as
            # Approved, and a mail failure does not roll back
            # the approval itself.
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })

            record.message_post(
                body=(
                    '<b>Leave Request Approved</b><br/>'
                    f'Approved by: <b>{self.env.user.name}</b><br/>'
                    'Status changed from Pending Approval to Approved.'
                ),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # =================================================
            # 2. SEND EMAIL ONLY AFTER APPROVAL
            # =================================================
            mail_sent = record._send_leave_email_to_students()

            if mail_sent:
                record.message_post(
                    body=(
                        '<b>Student Email Result</b><br/>'
                        'Student notification emails were sent successfully '
                        'after approval.'
                    ),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )
            else:
                # Approval remains Approved. The failure is recorded
                # in chatter instead of undoing the HOD decision.
                record.message_post(
                    body=(
                        '<b>Student Email Result</b><br/>'
                        'Leave is <b>Approved</b>, but no student email '
                        'was successfully sent. Please check the email '
                        'configuration and the email log.'
                    ),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

    # =========================================================
    # RESET
    # =========================================================

    def action_reset_draft(self):

        # Only HOD can reset
        if not self.env.user.has_group(
            'students_management.group_student_hod'
        ):
            raise UserError(
                'Only the HOD can reset a leave request.'
            )

        for record in self:

            record.write({
                'state': 'draft',
                'approved_by': False,
                'approved_date': False,
            })

            record.message_post(
                body='Leave request reset to Draft.',
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

    # =========================================================
    # SEND EMAIL
    # ONLY THIS TEACHER'S STUDENTS
    # =========================================================

    def _send_leave_email_to_students(self):

        self.ensure_one()

        # Find email template
        template = self.env.ref(
            'students_management.email_template_teacher_leave',
            raise_if_not_found=False,
        )

        if not template:

            self.message_post(
                body=(
                    '<b>Email NOT sent</b><br/>'
                    'Teacher Leave email template was not found.'
                ),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            return False

        # ONLY students belonging to this teacher
        students = self.env['student.student'].search([
            ('teacher_id', '=', self.teacher_id.id)
        ])

        if not students:

            self.message_post(
                body=(
                    '<b>Email NOT sent</b><br/>'
                    'No students found for teacher '
                    f'<b>{self.teacher_id.name}</b>.'
                ),
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            return False

        sent = []
        skipped = []
        failed = []

        # Get outgoing mail server
        mail_server = self.env[
            'ir.mail_server'
        ].sudo().search(
            [],
            limit=1
        )

        smtp_from = (
            mail_server.smtp_user
            if mail_server
            else False
        )

        # Send to every student
        for student in students:

            if not student.email:

                skipped.append(
                    f'{student.name} - No email address'
                )

                continue

            try:

                email_values = {
                    'email_to': student.email,
                }

                if smtp_from:
                    email_values['email_from'] = smtp_from

                mail_id = template.send_mail(
                    self.id,
                    force_send=True,
                    email_values=email_values,
                )

                mail = self.env[
                    'mail.mail'
                ].sudo().browse(mail_id)

                if mail.state == 'exception':

                    failed.append(
                        f'{student.name} ({student.email}) - '
                        f'{mail.failure_reason or "Unknown error"}'
                    )

                else:

                    sent.append(
                        f'{student.name} ({student.email})'
                    )

            except Exception as exc:

                failed.append(
                    f'{student.name} ({student.email}) - {exc}'
                )

        # =====================================================
        # CHATTER RESULT
        # =====================================================

        summary = []

        if sent:

            summary.append(
                '<b>Student emails sent:</b><br/>'
                + '<br/>'.join(sent)
            )

        if skipped:

            summary.append(
                '<b>Skipped:</b><br/>'
                + '<br/>'.join(skipped)
            )

        if failed:

            summary.append(
                '<b>Failed:</b><br/>'
                + '<br/>'.join(failed)
            )

        self.message_post(
            body=(
                '<br/><br/>'.join(summary)
                or 'No emails were processed.'
            ),
            message_type='comment',
            subtype_xmlid='mail.mt_note',
        )

        # At least one student email must be successfully sent
        return bool(sent)