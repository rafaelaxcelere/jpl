# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ChangeTask(models.TransientModel):
    _name = 'change.task.wizard'
    _description = 'Wizard for Change task'

    @api.model
    def _default_plant(self):
        user = self.env.user
        rel_plant = self.env["jpl_prod.plant_table"].search([("responsable", "=", user.id)], limit=1)
        return rel_plant if rel_plant else None

    plant_id = fields.Many2one('jpl_prod.plant_table', string='Plant', required=True, readonly=True,
                               default=_default_plant)
    from_task_id = fields.Many2one('hr.attendance.task', string='Task from', required=True)
    to_task_id = fields.Many2one('hr.attendance.task', string='Task to', required=True)
    pin = fields.Char(string='PIN', required=True)
    employee_ids = fields.Many2many('hr.employee', 'employee_change_task_id', string='Employees')

    @api.onchange('from_task_id')
    def _get_employees(self):
        obj_attendance = self.env["hr.attendance"]
        for rec in self:
            rec.employee_ids = False
            employees_lines = obj_attendance.search(
                [("attendance_task", "=", self.from_task_id.id), ("check_out", "=", False)]).mapped('employee_id')
            if employees_lines:
                return {'domain': {'employee_ids': [('id', '=', employees_lines.ids)]}}
            else:
                return {'domain': {'employee_ids': [('id', '=', [])]}}

    @api.multi
    def valid_user_pin(self):
        try:
            self.env.user.sudo(self._uid).check_credentials(self.pin)
        except:
            return False
        return True

    # @api.onchange('pin')
    # def _onchange_pin(self):
    #     if self.pin and not self.valid_user_pin():
    #         raise ValidationError(_('Error! Invalid pin.'))

    # @api.constrains('pin')
    # def _check_pin(self):
    #     for r in self:
    #         r._onchange_pin()

    @api.onchange('from_task_id', 'to_task_id')
    def _onchange_from_to_task(self):
        if self.from_task_id and self.to_task_id and self.from_task_id.id == self.to_task_id.id:
            raise ValidationError(_('To task must diferent to from task.'))

    @api.constrains('from_task_id', 'to_task_id')
    def _check_from_to_task(self):
        for r in self:
            r._onchange_from_to_task()

    @api.multi
    def make_change_task_wizard(self):
        self.ensure_one()
        if self.from_task_id and self.to_task_id and self.from_task_id.id != self.to_task_id.id:
            rel_attendance = self.env["hr.attendance"].search(
                [("attendance_task", "=", self.from_task_id.id), ("check_out", "=", False)])
            date_now = fields.Datetime.now()
            if rel_attendance:
                rel_attendance.write({"check_out": date_now})
                if self.employee_ids:
                    for employee in self.employee_ids:
                        matched_attendance = rel_attendance.filtered(lambda a: a.employee_id == employee)
                        if matched_attendance:
                            self.env["hr.attendance"].sudo().create({
                                'employee_id': matched_attendance.employee_id.id,
                                'check_in': date_now,
                                'attendance_task': self.to_task_id.id,
                            })
                            matched_attendance.employee_id.attendance_task = self.to_task_id.id
                else:
                    raise ValidationError(_('Debe seleccionar un empleado.'))
        menu = self.env['ir.ui.menu'].sudo().search(
            [('id', '=', self.env.ref("hr_attendance.menu_hr_attendance_view_attendances").id)])[:1]
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }
