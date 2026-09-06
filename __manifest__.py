# -*- coding: utf-8 -*-
{
    'name': 'Student Management',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage student details - name, age, and department',
    'description': """
Student Management
===================
A simple Odoo 19 application to store and manage student records
including Name, Age, and Department.
    """,
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',

    # Module dependencies
    'depends': ['base', 'mail', 'sale'],

    # Data files loaded on module install/update
 'data': [
    'security/student_security.xml',
    'security/ir.model.access.csv',

    'models/data/teacher_leave_sequence.xml',
    'models/data/teacher_leave_mail.xml',

    'wizard/assign_department_wizard_views.xml',
    'wizard/bulk_update_wizard_views.xml',
    'wizard/send_email_wizard_views.xml',
    'wizard/print_confirm_wizard_views.xml',

    'reports/student_report.xml',
    'reports/sale_order_report.xml',

    'views/student_views.xml',
    'views/department_views.xml',
    'views/subject_views.xml',
    'views/fee_structure_views.xml',
    'views/semester_views.xml',
    'views/teacher_views.xml',
    'views/teacher_leave_views.xml',
    'views/sale_order_views.xml',
],
    'installable': True,
    'application': True,   # Shows up as an app in Apps menu
    'auto_install': False,
}