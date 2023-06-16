# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models

import logging

logger = logging.getLogger(__name__)
try:
    # import unicodecsv
    import csv
except ImportError:
    logger.debug('Cannot import csv')


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def crud(self, values):
        employee_to_update = self.env['hr.employee'].with_context(active_test=False).search([
            ('barcode', '=', values.get('barcode')), ('company_id', '=', values.get('company_id'))], limit=1)
        task_id = self.env['hr.attendance.task'].search([('id_activity', '=', values.get('attendance_task', 0))],
                                                        limit=1)

        if employee_to_update and values.get('check_in'):
            employee_id = employee_to_update.id
            check_in = (values.get("check_in"))
            check_out = (values.get("check_out")) if values.get("check_out") else None
            attendance_task = task_id.id if task_id else None
            att_obj = self.search([('employee_id', '=', employee_id), ('check_in', '=', check_in)], limit=1)
            if not att_obj:
                self.sudo().create({
                    'employee_id': employee_id,
                    'check_in': check_in,
                    'check_out': check_out,
                    'attendance_task': attendance_task,
                    'company_id': values.get("company_id"),
                })
