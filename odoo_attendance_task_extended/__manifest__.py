# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Attendance/Time Tracking With Task Details (Enhanced)",
    "summary": "Attendance/Time Tracking With Task Details (Enhanced)",
    "category": "Human Resources",
    "version": "1.0",
    "author": "ASOLUTIONS",
    "website": "",
    "description": """Attendance/Time Tracking With Task Details upon Check In/Check Out.""",
    "depends": ['base', 'web', 'hr', 'hr_attendance', 'jpl_productivity2_2'],
    "data": [
	'security/hr_attendance_security.xml',
        'data/ir_cron.xml',
        'data/email_template.xml',
        'security/delete_access_record.xml',
        'security/ir.model.access.csv',        
        'views/hr_employee_views.xml',
        'views/filters_groupby_menu.xml',
        'views/hr_attendance_task_views.xml',
        'views/hr_attendance_views.xml',
        'views/time_control_views.xml',
        'views/hr_holidays_status.xml',
        'views/alert_logs_views.xml',
        'wizard/wizard_change_task_view.xml',
    ],
    'qweb': ['static/src/xml/attendance.xml'],
    # 'images':['images/Banner_Image.png'],
    "installable": True,
    "auto_install": False,
    "price": 0,
    "currency": "EUR",
	'license': 'AGPL-3'

}
