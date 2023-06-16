# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.tools.sql import drop_view_if_exists
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import pytz
import math

@api.model
def _tz_get(self):
    # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
    return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    attendance_task = fields.Many2one('hr.attendance.task', string="Task")
    id_activity = fields.Integer(related='attendance_task.id_activity', string="Activity", store=True, readonly=True)
    type = fields.Selection(related='attendance_task.type', string="Type Process", store=True, readonly=True)
    related_plant = fields.Many2one(related='attendance_task.related_plant', string="Related Plant", store=True,
                                    readonly=True)
    workedHours = fields.Float(string='Worked hours', digits=(4, 2))

    employee_category = fields.Many2one(related='employee_id.employee_category')
    employee_status = fields.Many2one(related='employee_id.employee_status')
    start_day6am_on_checkin = fields.Boolean(compute='_compute_start_day', string="start_day_6am", store=True,
                                             required=True)
    start_day_hour_on_check_in = fields.Integer(compute='_compute_hours_today')
    start_day_minute_on_check_in = fields.Integer(compute='_compute_hours_today')
    hours_today = fields.Float(compute='_compute_hours_today')
    sended_alert = fields.Boolean(default=False)
    sended_alert_2hours = fields.Boolean(default=False)

    @api.constrains('related_plant')
    def check_unique_date(self):
        for rec in self:
            if not rec.related_plant:
                raise ValidationError(_(
                    'Para generar un registro, se ha de especificar la tarea'))
            else:
                if rec.related_plant.tz != rec.employee_id.tz:
                    raise ValidationError(_(
                        'Las zonas horarias del empleado y la planta de la tarea en la que se está intentando fichar no coinciden.'))

    @api.model
    def _cron_send_alert_2(self):
        records_to_send_2 = {}
        today = fields.date.today()
        week_num = today.weekday()
        week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                     "Saturday", "Sunday"]
        dom = [
            ('sended_alert_2hours', '=', False),
            ('check_in', '>=',
             datetime.now().replace(hour=0, minute=0, second=0).strftime(
                 '%Y-%m-%d %H:%M:%S')),
            ('check_out', '=', False)
        ]

        hr_attendances = self.env['hr.attendance'].search(dom)
        for hr_att in hr_attendances:
            # sobre paso de 2 horas contratadas en el dia
            hour, minute = divmod(hr_att.hours_today, 1)
            minute *= 60
            if week_days[week_num] == "Monday":
                if hr_att.employee_id.mon_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.mon_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.mon_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Lunes'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Tuesday":
                if hr_att.employee_id.tue_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.tue_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.tue_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Martes'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Wednesday":
                if hr_att.employee_id.wed_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.wed_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.wed_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Miercoles'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Thursday":
                if hr_att.employee_id.thu_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.thu_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.thu_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Jueves'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Friday":
                if hr_att.employee_id.fri_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.fri_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.fri_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Viernes'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Saturday":
                if hr_att.employee_id.sat_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.sat_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.sat_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Sabado'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

            if week_days[week_num] == "Sunday":
                if hr_att.employee_id.sun_hour_contract != 0.0:
                    hour_contrat, minute_contract = divmod(hr_att.employee_id.sun_hour_contract, 1)
                    minute_contract *= 60

                    if (hour > (2 + hour_contrat)) or (hour == (2 + hour_contrat) and minute >= minute_contract):
                        rest_hours = hr_att.hours_today - hr_att.employee_id.sun_hour_contract
                        hour_rest, minute_rest = divmod(rest_hours, 1)
                        minute_rest *= 60
                        vals = {
                            'name': hr_att.employee_id.name,
                            'hours': '{0:02.0f}:{1:02.0f}'.format(hour_rest, minute_rest),
                            'day': _('Domingo'),
                            'date': fields.Datetime.from_string(
                                hr_att.create_date).strftime('%d/%m/%Y'),
                            'employee_id': hr_att.employee_id,
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                            'related_plant': hr_att.related_plant.id
                        }
                        if hr_att.related_plant.responsable:
                            records_to_send_2.setdefault(
                                hr_att.related_plant.responsable, []).append(
                                vals)
                            hr_att.sended_alert_2hours = True

        self._send_alert_2(records_to_send_2)

    @api.model
    def _cron_send_alert(self):
        records_to_send_11_45 = {}
        dom = [
            ('sended_alert', '=', False),
            ('check_in', '>=',
             datetime.now().replace(hour=0, minute=0, second=0).strftime(
                 '%Y-%m-%d %H:%M:%S')),
            ('check_out', '=', False)
        ]
        hr_attendances = self.env['hr.attendance'].search(dom).filtered(lambda x: x.hours_today > 11.45)
        for hr_att in hr_attendances:
            # sobrepaso de 11:45 de trabajo en el dia
            hour, minute = divmod(hr_att.hours_today, 1)
            minute *= 60
            if (hour > 11) or (hour >= 11 and minute > 45):
                vals = {
                    'name': hr_att.employee_id.name,
                    'hours': '{0:02.0f}:{1:02.0f}'.format(
                        *divmod(hr_att.hours_today * 60, 60)),
                    'date': fields.Datetime.from_string(
                        hr_att.create_date).strftime('%d/%m/%Y'),
                    'employee_id': hr_att.employee_id,
                    'worked_hours': '{0:02.0f}:{1:02.0f}'.format(hour, minute),
                    'related_plant': hr_att.related_plant.id
                }
                if hr_att.related_plant.responsable:
                    records_to_send_11_45.setdefault(hr_att.related_plant.responsable, []).append(vals)
                    hr_att.sended_alert = True
                hr_att.employee_id.attendance_state == 'checked_out'
        self._send_alert_11_45(records_to_send_11_45)

    def _send_alert_2(self, records_to_send):
        for responsible, records in records_to_send.iteritems():
            for record in records:
                vals = {
                    'name': _('El empleado %s ha excedido en '
                              '%s horas las horas de contrato para el %s.') % (record.get('name', ''),
                                                                          record.get('hours'),
                                                                          record.get('day')),
                    'employee_id': record.get('employee_id', self.env['hr.employee']).id,
                    'worked_hours': record.get('worked_hours', ''),
                    'related_plant': record.get('related_plant', False)
                }
                self.env['jpl.alert.logs'].create(vals)
            ctx = dict()
            ctx.update(
                {
                    'records': records
                }
            )
            if record.get('employee_id', self.env['hr.employee']).plant_id.active_emails:
                template = self.env.ref(
                    'odoo_attendance_task_extended.template_notification_alert_2_hours')

                template.with_context(ctx).send_mail(responsible.partner_id.id,
                                                      force_send=True)
        return True

    def _send_alert_11_45(self, records_to_send):
        for responsible, records in records_to_send.iteritems():
            for record in records:
                vals = {
                    'name': _('The employee %s has exceeded the limit of '
                              '11:45 working hours in the day %s. Has '
                              'reported %s hours.') % (record.get('name', ''),
                                                       record.get('date'),
                                                       record.get('worked_hours')),
                    'employee_id': record.get('employee_id', self.env['hr.employee']).id,
                    'worked_hours': record.get('worked_hours', ''),
                    'related_plant': record.get('related_plant', False)
                }
                self.env['jpl.alert.logs'].create(vals)
            ctx = dict()
            ctx.update(
                {
                    'records': records
                }
            )
            if record.get('employee_id', self.env['hr.employee']).plant_id.active_emails:
                template = self.env.ref(
                    'odoo_attendance_task_extended.template_notification_alert')

                template.with_context(ctx).send_mail(responsible.partner_id.id,
                                                      force_send=True)
        return True

    @api.multi
    @api.depends('check_in', 'check_out')
    def _compute_hours_today(self):
        for rec in self:

            hour_start = rec.related_plant.start_day_hour
            rec.start_day_hour_on_check_in = hour_start
            minute_start = rec.related_plant.start_day_minute
            rec.start_day_minute_on_check_in = minute_start

            # start of day in the employee's timezone might be the previous day in utc
            has_tz = rec.employee_id.user_id.tz or rec.employee_id.tz
            if has_tz:
                tz = pytz.timezone(rec.employee_id.user_id.tz or rec.employee_id.tz)
                if tz:
                    now_utc = datetime.utcnow()
                    now_tz = pytz.utc.localize(now_utc).astimezone(tz)
                    start_tz = now_tz + relativedelta.relativedelta(hour=hour_start, minute=minute_start, second=0)  # day start in the employee's timezone
                    if start_tz <= now_tz:
                        start_tz = now_tz + relativedelta.relativedelta(hour=hour_start, minute=minute_start, second=0)
                        start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
                    else:
                        start_tz = (now_tz - relativedelta.relativedelta(days=1)) + relativedelta.relativedelta(hour=hour_start, minute=minute_start,  second=0)
                        start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)

                    attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('check_in', '>=', start_naive.strftime('%Y-%m-%d %H:%M:%S'))])

                    worked_hours = 0
                    for attendance in attendances:
                        check_in = datetime.strptime(attendance.check_in, '%Y-%m-%d %H:%M:%S') if attendance.check_in else False
                        check_out = datetime.strptime(attendance.check_out, '%Y-%m-%d %H:%M:%S') if attendance.check_out else False
                        delta = (check_out or now_utc) - check_in
                        worked_hours += delta.total_seconds() / 3600.0
                    rec.hours_today = worked_hours
            else:
                if rec.employee_id:
                    raise UserError(_("El empleado o usuario asociado al empleado debe tener establecida una Zona Horaria."))

    @api.multi
    def read(self, fields=None, load='_classic_read'):
       result = super(HRAttendance, self).read(fields=fields, load=load)
       for rec in self:
           if not rec.check_out and not self.env.context.get('group_by_no_leaf', False):
               delta = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                         DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                   rec.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
               rec.worked_hours = round((delta.total_seconds() / 3600.0), 2)
       return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # args +=[('attendance_task.related_plant.active','in',[True, False])]
        ids = super(HRAttendance, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=False, access_rights_uid=access_rights_uid)
        return ids

    @api.depends('check_in')
    def _compute_start_day(self):
        for record in self:

            startday6am = record.related_plant.start_day_6am
            record.start_day6am_on_checkin = startday6am

            eum = pytz.timezone(record.related_plant.tz)
            start_check_in_hour = pytz.utc.localize(datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(
                eum).time()

            if startday6am == True:

                change_day_hour = time(hour=record.start_day_hour_on_check_in, minute=record.start_day_minute_on_check_in, second=0)

                if start_check_in_hour >= change_day_hour:

                    start_check_in = pytz.utc.localize(datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(eum).date()
                else:

                    start_check_in = pytz.utc.localize(datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(eum).date() - relativedelta.relativedelta(seconds=86400)
            else:

                change_day_hour = time(hour=record.start_day_hour_on_check_in, minute=record.start_day_minute_on_check_in, second=0)

                if start_check_in_hour >= change_day_hour:

                    start_check_in = pytz.utc.localize(
                        datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(
                        eum).date() + relativedelta.relativedelta(seconds=86400)
                else:

                    start_check_in = pytz.utc.localize(
                        datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(eum).date()


            record.start_date = start_check_in
            record.month = start_check_in.month
            record.year = start_check_in.year
            record.employee_category_on_checkin = record.employee_category
            record.employee_status_on_checkin = record.employee_status

    start_date = fields.Date(default=lambda self: fields.Date.today(), compute='_compute_start_day', required=True,
                             index=True,
                             store=True, ondelete='set null')
    month = fields.Integer(default=0, compute='_compute_start_day', required=True,
                             index=True,
                             store=True, ondelete='set null')
    year = fields.Integer(default=0, compute='_compute_start_day', required=True,
                           index=True,
                           store=True, ondelete='set null')
    employee_category_on_checkin = fields.Many2one('jpl_prod.employee_category', compute='_compute_start_day', string="employee_cat", store=True)
    employee_status_on_checkin = fields.Many2one('jpl_prod.employee_status', compute='_compute_start_day', string="employee_status", store=True)

    @api.depends('check_out')
    def _compute_check_out_control(self):
        for rec in self:
            now_utc = datetime.utcnow()
            rec.check_out_control = now_utc

    check_out_control = fields.Datetime(compute=_compute_check_out_control, store=True)

    @api.depends('employee_category_on_checkin', 'employee_status_on_checkin', 'related_plant', 'worked_hours')
    def _compute_employee_cost(self):
        for record in self:
            emp_cost_on_month_cat_and_status = self.env['jpl_prod.cost_table'].search(
                [('id_plant', '=', record.related_plant.id),
                 ('id_category_employee', '=', record.employee_category_on_checkin.id),
                 ('id_status_employee', '=', record.employee_status_on_checkin.id),
                 ('month', '=', record.month),
                 ('year', '=', record.year)], limit=1).cost
            if emp_cost_on_month_cat_and_status:
                record.employee_cost = emp_cost_on_month_cat_and_status
            else:
                emp_cost_on_month_cat_and_status = record.related_plant.cost
                record.employee_cost = emp_cost_on_month_cat_and_status

            record.activity_cost = record.worked_hours * emp_cost_on_month_cat_and_status

    employee_cost = fields.Float(compute='_compute_employee_cost', store=True, string='employee cost')

    activity_cost = fields.Float(compute='_compute_employee_cost', store=True, string='activity cost')

    #variables para Time Control

    theoretical_hours = fields.Float(string='Horas_Teoricas', default=0.0)
    presence_hours_1 = fields.Float(compute='_compute_presence_day', string='Horas_presencia_1', store=True, required=True, default=0.0)
    presence_type_1 = fields.Text(string='Tipo_presencia_1', default="D", store=True, required=True)
    presence_hours_2 = fields.Float(compute='_compute_presence_day', string='Horas_presencia_2', store=True, required=True, default=0.0)
    presence_type_2 = fields.Text(string='Tipo_presencia_2', default="N", store=True, required=True)

    start_day_presence_hour = fields.Integer(string='Hora inicio dia', default=6, store=True, required=True)
    end_day_presence_hour = fields.Integer(string='Hora Fin dia', default=22, store=True, required=True)

    @api.depends('check_in', 'check_out')
    def _compute_presence_day(self):
        for record in self:
            if record.check_out:
                eum = pytz.timezone(record.related_plant.tz)

                start_datetime = pytz.utc.localize(datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(eum)
                end_datetime = pytz.utc.localize(datetime.strptime(record.check_out, '%Y-%m-%d %H:%M:%S')).astimezone(
                    eum)
                record.check_in_with_tz = start_datetime
                record.check_out_with_tz = end_datetime


                start_day_presence_hour = start_datetime.replace(hour=record.start_day_presence_hour, minute=00, second=00)
                end_day_presence_hour = start_datetime.replace(hour=record.end_day_presence_hour, minute=00, second=00)

                employee_check_in = pytz.utc.localize(datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')).astimezone(
                    eum)
                employee_check_out = pytz.utc.localize(datetime.strptime(record.check_out, '%Y-%m-%d %H:%M:%S')).astimezone(
                    eum)

                if start_day_presence_hour > employee_check_in:

                    if start_day_presence_hour > employee_check_out:

                        delta_night = employee_check_out - employee_check_in

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                    if end_day_presence_hour > employee_check_out > start_day_presence_hour:

                        delta_night = start_day_presence_hour - employee_check_in

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                        delta_day = employee_check_out - start_day_presence_hour

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                    if employee_check_out > end_day_presence_hour:

                        delta_night = (employee_check_out - end_day_presence_hour)+(start_day_presence_hour-employee_check_in)

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                        delta_day = end_day_presence_hour - start_day_presence_hour

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                if end_day_presence_hour > employee_check_in >= start_day_presence_hour:

                    if end_day_presence_hour > employee_check_out:

                        delta_day = employee_check_out - employee_check_in

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                    if (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)) > employee_check_out >= end_day_presence_hour:

                        delta_night = employee_check_out - end_day_presence_hour

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                        delta_day = end_day_presence_hour - employee_check_in

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                    if employee_check_out > (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)):

                        delta_night = (start_day_presence_hour + relativedelta.relativedelta(seconds=86400))-end_day_presence_hour

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                        delta_day = (end_day_presence_hour - employee_check_in) + (employee_check_out - (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)))

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                if employee_check_in >= end_day_presence_hour:

                    if (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)) > employee_check_out:

                        delta_night = employee_check_out - employee_check_in

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                    if (end_day_presence_hour + relativedelta.relativedelta(seconds=86400)) > employee_check_out >= (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)):

                        delta_day = employee_check_out - (start_day_presence_hour + relativedelta.relativedelta(seconds=86400))

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

                        delta_night = (start_day_presence_hour + relativedelta.relativedelta(seconds=86400)) - employee_check_in

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                    if employee_check_out > (end_day_presence_hour + relativedelta.relativedelta(seconds=86400)):

                        delta_night = ((start_day_presence_hour + relativedelta.relativedelta(seconds=86400)) - employee_check_in)+(employee_check_out-(end_day_presence_hour + relativedelta.relativedelta(seconds=86400)))

                        record.presence_hours_2 = delta_night.total_seconds() / 3600.0

                        delta_day = (end_day_presence_hour + relativedelta.relativedelta(seconds=86400))-(start_day_presence_hour + relativedelta.relativedelta(seconds=86400))

                        record.presence_hours_1 = delta_day.total_seconds() / 3600.0

    check_in_with_tz = fields.Datetime(compute=_compute_presence_day, store=True)
    check_out_with_tz = fields.Datetime(compute=_compute_presence_day, store=True)

    @api.model
    def create(self, vals):
        if 'check_in' in vals and self._context.get('new_task_id'):
            vals.update({'attendance_task': self._context.get('new_task_id')})
        res = super(HRAttendance, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        for rec in self:
            check_in = 'check_in' in values and values.get(
                'check_in') or rec.check_in
            check_out = 'check_out' in values and values.get(
                'check_out') or rec.check_out
            if check_in and check_out:
                checkIn = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
                checkOut = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                wh = round((checkOut - checkIn).total_seconds() / 3600, )
                values['workedHours'] = wh
        return super(HRAttendance, self).write(values)

    def add_employee_task(self, task_id, task, emp_id=False):
        if not task_id and task:
            res = self.env['hr.attendance.task'].create({
                'name': task
            })
            if not(self.aux_create_attendance(res.id)):
                self.write({
                    'attendance_task': res.id
                })
                self.employee_id.write({
                    'attendance_task': res.id
                })
        elif not task and task_id:
            if not(self.aux_create_attendance(task_id)):
                self.write({
                    'attendance_task': task_id
                })
                self.employee_id.write({
                    'attendance_task': task_id
                })
        elif task_id and task:
            task_obj = self.env['hr.attendance.task'].search(
                [('id', '=', task_id)])

            if task_obj.name == task:
                if not (self.aux_create_attendance(task_id)):
                    self.write({
                        'attendance_task': task_id
                    })
                    self.employee_id.write({
                        'attendance_task': task_id
                    })
            else:
                res = self.env['hr.attendance.task'].create({
                    'name': task
                })
                if not (self.aux_create_attendance(task_id)):
                    self.write({
                        'attendance_task': res.id
                    })
                    self.employee_id.write({
                        'attendance_task': res.id
                    })

    def aux_create_attendance(self, task_id):
        if self.employee_id.last_attendance_id.attendance_task and self.employee_id.last_attendance_id.attendance_task.id != task_id:
            action_date = datetime.now() + relativedelta.relativedelta(seconds=1)
            res = self.create(vals={
                'employee_id': self.employee_id.id,
                'check_in': action_date,
                'attendance_task': task_id,
            })
            self.employee_id.attendance_task = task_id
            return res
        return False

    def _compute_holiday_by_absence(self):
        today = fields.date.today()
        yesterday_date = today - relativedelta.relativedelta(days=1)
        yesterday = datetime.combine(yesterday_date, datetime.min.time())
        week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                     "Saturday", "Sunday"]
        week_num = yesterday.weekday()
        domain = [
            ('name', '=', 'AI - Ausencia injustificada')
        ]
        unjustified_absence = self.env['hr.holidays.status'].search(
            domain, limit=1)
        employees = self.env['hr.employee'].sudo().search([('employee_status.name', '=', 'I')])
        for employee in employees:
            tz = pytz.timezone(
                employee.user_id.tz or employee.tz or 'Europe/Madrid')
            dom_att = [
                ('employee_id', '=', employee.id)
            ]
            attendance = self.env['hr.attendance'].search(dom_att).filtered(
                lambda x: x.start_date
                      and fields.Datetime.from_string(x.start_date).date() == yesterday
            )

            holidays = self.env['hr.holidays'].search(dom_att).filtered(
                lambda x: x.date_from and x.date_to
                          and fields.Datetime.from_string(x.date_from).date() == yesterday_date
                          and fields.Datetime.from_string(x.date_to).date() == yesterday_date
            )
            if not attendance:
                if not holidays:
                    if week_days[week_num] == "Monday":
                        if employee.mon_hour_contract != 0.0:
                            hour, minute = divmod(employee.mon_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Tuesday":
                        if employee.tue_hour_contract != 0.0:
                            hour, minute = divmod(employee.tue_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Wednesday":
                        if employee.wed_hour_contract != 0.0:
                            hour, minute = divmod(employee.wed_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Thursday":
                        if employee.thu_hour_contract != 0.0:
                            hour, minute = divmod(employee.thu_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Friday":
                        if employee.fri_hour_contract != 0.0:
                            hour, minute = divmod(employee.fri_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Saturday":
                        if employee.sat_hour_contract != 0.0:
                            hour, minute = divmod(employee.sat_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)

                    elif week_days[week_num] == "Sunday":
                        if employee.sun_hour_contract != 0.0:
                            hour, minute = divmod(employee.sun_hour_contract, 1)
                            minute *= 60
                            if tz:
                                yes = pytz.utc.localize(yesterday).astimezone(tz)
                                date_from = yes.replace(hour=6)
                                date_to = yes.replace(hour=6 + int(hour),
                                                      minute=int(minute))
                            else:
                                date_from = yesterday.replace(hour=6)
                                date_to = yesterday.replace(hour=6 + int(hour),
                                                            minute=int(minute))
                            vals = {
                                'holiday_status_id': unjustified_absence.id,
                                'employee_id': employee.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'number_of_days_temp': 1
                            }
                            self.env['hr.holidays'].sudo().create(vals)


class HolidaysType(models.Model):
    _inherit = 'hr.holidays.status'

    x100_cost = fields.Float(string='Porcentaje Coste', default=100.0)


class Holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    @api.depends('date_from')
    def _compute_employee_attributes(self):
        for rec in self:

            rec.plant_id = rec.employee_id.plant_id
            rec.employee_category_on_checkin = rec.employee_id.employee_category
            rec.employee_status_on_checkin = rec.employee_id.employee_status

            if rec.date_from and rec.plant_id:
                eum = pytz.timezone(rec.plant_id.tz)
                start_day = pytz.utc.localize(datetime.strptime(rec.date_from, '%Y-%m-%d %H:%M:%S')).astimezone(eum).date()

                rec.start_date = start_day
                rec.month = start_day.month
                rec.year = start_day.year

                emp_cost_on_month_cat_and_status = self.env['jpl_prod.cost_table'].search(
                    [('id_plant', '=', rec.plant_id.id),
                     ('id_category_employee', '=', rec.employee_category_on_checkin.id),
                     ('id_status_employee', '=', rec.employee_status_on_checkin.id),
                     ('month', '=', rec.month),
                     ('year', '=', rec.year)], limit=1).cost
                if emp_cost_on_month_cat_and_status:
                    rec.employee_cost = emp_cost_on_month_cat_and_status
                else:
                    emp_cost_on_month_cat_and_status = rec.plant_id.cost
                    rec.employee_cost = emp_cost_on_month_cat_and_status

    plant_id = fields.Many2one('jpl_prod.plant_table', compute=_compute_employee_attributes, string="Plant", store=True)

    employee_category_on_checkin = fields.Many2one('jpl_prod.employee_category', compute=_compute_employee_attributes,
                                                   string="Employee Category", store=True)
    employee_status_on_checkin = fields.Many2one('jpl_prod.employee_status', compute=_compute_employee_attributes,
                                                 string="Employee Status", store=True)
    start_date = fields.Date(default=lambda self: fields.Date.today(), compute=_compute_employee_attributes, required=True,
                             index=True,
                             store=True, ondelete='set null')
    month = fields.Integer(default=0, compute=_compute_employee_attributes, required=True,
                           index=True,
                           store=True, ondelete='set null')
    year = fields.Integer(default=0, compute=_compute_employee_attributes, required=True,
                          index=True,
                          store=True, ondelete='set null')
    employee_cost = fields.Float(compute=_compute_employee_attributes, store=True, string='employee cost')


class time_control_table(models.Model):
        _name = 'jpl_prod.time_control_table'
        _auto = False

        id = fields.Many2one(comodel_name='hr.attendance', readonly=True)
        date = fields.Date(readonly=True)
        employee_id = fields.Many2one(comodel_name='hr.employee', string="Nombre", readonly=True)
        id_sap = fields.Integer(string='ID Empleado', readonly=True)
        dni = fields.Char(string='DNI', readonly=True)
        related_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
        horas_teoricas = fields.Float(string='Horas Teóricas', readonly=True)
        horas_presencia_1 = fields.Float(string='Horas Presencia 1', readonly=True)
        tipo_presencia_1 = fields.Char(string='Tipo Presencia 1', readonly=True)
        horas_presencia_2 = fields.Float(string='Horas Presencia 2', readonly=True)
        tipo_presencia_2 = fields.Char(string='Tipo Presencia 2', readonly=True)
        horas_trabajadas = fields.Float(string='Presencia Total', readonly=True)
        horas_presencia_1_red = fields.Float(string='Horas Presencia 1 Red', readonly=True)
        horas_presencia_2_red = fields.Float(string='Horas Presencia 2 Red', readonly=True)
        horas_trabajadas_red = fields.Float(string='Presencia Total Red', readonly=True)
        horas_ausencia_1 = fields.Float(string='Horas Ausencia 1', readonly=True)
        tipo_ausencia_1 = fields.Char(string='Tipo Ausencia 1', readonly=True)
        descripcion_ausencia = fields.Char(string='Descripcion Ausencia 1', readonly=True)

        @api.model_cr
        def init(self):
            drop_view_if_exists(self._cr, 'jpl_prod_time_control_table')
            self._cr.execute(""" CREATE VIEW jpl_prod_time_control_table AS (
            with cte as (select 
                            (1000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 1 <= number_of_days_temp 
                            union all
                            select
                            (2000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '1' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1) * interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 2 <= number_of_days_temp 
                            union all
                            select
                            (3000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '2' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1) * interval'1' day))))/3600 as hours_Day,
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 3 <= number_of_days_temp 
                            union all
                            select
                            (4000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '3' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1) * interval'1' day))))/3600 as hours_Day,
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 4 <= number_of_days_temp 
                            union all
                            select
                            (5000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '4' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 5 <= number_of_days_temp
                            union all
                            select
                            (6000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '5' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 6 <= number_of_days_temp
                            union all
                            select
                            (7000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '6' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 7 <= number_of_days_temp
                            union all
                            select
                            (8000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '7' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 8 <= number_of_days_temp
                            union all
                            select
                            (9000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '8' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 9 <= number_of_days_temp
                            union all
                            select
                            (10000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '9' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 10 <= number_of_days_temp
                            union all
                            select
                            (11000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '10' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 11 <= number_of_days_temp
                            union all
                            select
                            (12000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '11' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 12 <= number_of_days_temp
                            union all
                            select
                            (13000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '12' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 13 <= number_of_days_temp
                            union all
                            select
                            (14000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '13' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 14 <= number_of_days_temp
                            union all
                            select
                            (15000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '14' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 15 <= number_of_days_temp
                            union all
                            select
                            (16000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '15' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 16 <= number_of_days_temp
                            union all
                            select
                            (17000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '16' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 17 <= number_of_days_temp
                            union all
                            select
                            (18000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '17' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 18 <= number_of_days_temp
                            union all
                            select
                            (19000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '18' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 19 <= number_of_days_temp
                            union all
                            select
                            (20000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '19' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 20 <= number_of_days_temp
                            union all
                            select
                            (21000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '20' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 21 <= number_of_days_temp
                            union all
                            select
                            (22000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '21' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 22 <= number_of_days_temp
                            union all
                            select
                            (23000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '22' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 23 <= number_of_days_temp
                            union all
                            select
                            (24000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '23' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 24 <= number_of_days_temp
                            union all
                            select
                            (25000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '24' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 25 <= number_of_days_temp
                            union all
                            select
                            (26000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '25' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 26 <= number_of_days_temp
                            union all
                            select
                            (27000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '26' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 27 <= number_of_days_temp
                            union all
                            select
                            (28000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '27' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 28 <= number_of_days_temp
                            union all
                            select
                            (29000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '28' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 29 <= number_of_days_temp
                            union all
                            select
                            (30000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '29' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 30 <= number_of_days_temp
                            union all
                            select
                            (31000000000 + hh.id) as id, 
                            hh.date_from as d_from, 
                            hh.date_to as d_to, 
                            date(hh.date_from + interval '30' day) as start_date,
                            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
                            hh.holiday_status_id, 
                            hh.employee_id, 
                            hh.number_of_days_temp, 
                            hs.name,
                            hs.x100_cost,
                            he.barcode,
                            he.identification_id,
                            he.plant_id
                            from public.hr_holidays as hh
                            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
                            inner join public.hr_employee as he on (hh.employee_id = he.id)
                            where 31 <= number_of_days_temp)
                            Select 
                            id,
                            start_date as date,
                            employee_id as employee_id,
                            barcode as id_sap,
                            identification_id as dni,
                            plant_id as related_plant,
                            0 as horas_teoricas,
                            0 as horas_presencia_1,
                            'D' as tipo_presencia_1,
                            0 as horas_presencia_2,
                            'N' as tipo_presencia_2,
                            0 as horas_trabajadas,
                            0 as horas_presencia_1_red,
                            0 as horas_presencia_2_red,
                            0 as horas_trabajadas_red,
                            hours_day as horas_ausencia_1,
                            left(name,3) as tipo_ausencia_1,
                            name as descripcion_ausencia
                            from cte
                            union all
                            select
                            min(att.id) as id,
                            att.start_date as date,
                            emp.id as employee_id,
                            emp.barcode as id_sap,
                            emp.identification_id as dni,
                            att.related_plant,
                            sum(att.theoretical_hours) as horas_teoricas,
                            sum(att.presence_hours_1) as horas_presencia_1,
                            'D' as tipo_presencia_1,
                            sum(att.presence_hours_2) as horas_presencia_2,
                            'N' as tipo_presencia_2,
                            sum(att.worked_hours) as horas_trabajadas,
                            (case 	when (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) <= 0.125 then (floor(sum(att.presence_hours_1))) else 
                            (case 	when 0.125 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.375 then (floor(sum(att.presence_hours_1))+0.25)else 
                            (case 	when 0.375 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.625 then (floor(sum(att.presence_hours_1))+0.50)else 
                            (case 	when 0.625 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.875 then (floor(sum(att.presence_hours_1))+0.75)else 
                            (case 	when 0.875 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) then (ceiling(sum(att.presence_hours_1))) else 
                            0.00 end)end)end)end)end) as horas_presencia_1_red,
                            (case 	when (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) <= 0.125 then (floor(sum(att.presence_hours_2))) else 
                            (case 	when 0.125 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.375 then (floor(sum(att.presence_hours_2))+0.25)else 
                            (case 	when 0.375 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.625 then (floor(sum(att.presence_hours_2))+0.50)else 
                            (case 	when 0.625 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.875 then (floor(sum(att.presence_hours_2))+0.75)else 
                            (case 	when 0.875 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) then (ceiling(sum(att.presence_hours_2))) else 
                            0.00 end)end)end)end)end) as horas_presencia_2_red,
                            (case 	when (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) <= 0.125 then (floor(sum(att.presence_hours_1))) else 
                            (case 	when 0.125 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.375 then (floor(sum(att.presence_hours_1))+0.25)else 
                            (case 	when 0.375 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.625 then (floor(sum(att.presence_hours_1))+0.50)else 
                            (case 	when 0.625 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) and (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) < 0.875 then (floor(sum(att.presence_hours_1))+0.75)else 
                            (case 	when 0.875 <= (sum(att.presence_hours_1)-floor(sum(att.presence_hours_1))) then (ceiling(sum(att.presence_hours_1))) else 
                            0.00 end)end)end)end)end) + (case 	when (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) <= 0.125 then (floor(sum(att.presence_hours_2))) else 
                            (case 	when 0.125 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.375 then (floor(sum(att.presence_hours_2))+0.25)else 
                            (case 	when 0.375 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.625 then (floor(sum(att.presence_hours_2))+0.50)else 
                            (case 	when 0.625 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) and (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) < 0.875 then (floor(sum(att.presence_hours_2))+0.75)else 
                            (case 	when 0.875 <= (sum(att.presence_hours_2)-floor(sum(att.presence_hours_2))) then (ceiling(sum(att.presence_hours_2))) else 
                            0.00 end)end)end)end)end) as horas_trabajadas_red,
                            0.00 as horas_ausencia_1,
                            null as tipo_ausencia_1,
                            null as descripcion_ausencia
                            from public.hr_attendance as att
                            inner join public.hr_employee as emp on (att.employee_id = emp.id)
                            inner join public.hr_attendance_task_view as tw on ( att.attendance_task = tw.id)
                            where tw.name not like '%|ntc|%'
                            group by att.start_date, emp.identification_id,emp.barcode,emp.id,att.related_plant
            )""")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    attendance_task = fields.Many2one('hr.attendance.task', string="Task")
    tz = fields.Selection(related='plant_id.tz', string="Zona horaria", store=True, readonly=True)
    last_attendance_id = fields.Many2one('hr.attendance', compute='_compute_last_attendance_id')
    is_check_in = fields.Boolean(compute='_compute_is_check_in_out_employee', store=True)

    @api.depends('attendance_state')
    def _compute_is_check_in_out_employee(self):
        for empleado in self:
            employee_check_in = self.env['hr.employee'].search([('id', '!=', empleado.id), ('attendance_state', '=', 'checked_in')])
            empleado.is_check_in = employee_check_in > 0 if empleado.attendance_state == 'checked_in' else False

    @api.multi
    def _compute_is_check_out_employee(self):
        data = self.env['hr.employee']

    @api.depends('attendance_ids')
    def _compute_last_attendance_id(self):
        for employee in self:
            employee.last_attendance_id = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
            ], limit=1)

    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_state(self):
        for employee in self:
            att = employee.last_attendance_id.sudo()
            employee.attendance_state = att and not att.check_out and 'checked_in' or 'checked_out'

    def check_employee_task(self):
        return self.attendance_task.name

    def get_employee_task(self):
        return {
            'name': self.attendance_task.name,
            'id': self.attendance_task.id
        }

    def get_old_and_new_task(self):
        res = {'in_task_id': self.attendance_task.id, 'in_task': self.attendance_task.name,
               'in_attendance': self.last_attendance_id.read() and self.last_attendance_id.read()[0] or False}
        check_out_attendances = self.attendance_ids.filtered(lambda x: x.check_in and x.check_out)
        if check_out_attendances:
            res['out_attendance'] = check_out_attendances.sorted(lambda x: x.check_out)[-1].read()[0]
            out_attendance_task = check_out_attendances.sorted(lambda x: x.check_out)[-1].attendance_task
            res['out_task'] = out_attendance_task.name
            res['out_task_id'] = out_attendance_task.id
        else:
            res['out_attendance'] = {}
            res['out_task'] = res['in_task']
            res['out_task_id'] = res['in_task_id']
        return res

    @api.multi
    def attendance_manual(self, next_action, entered_pin=None, task_id=None, task_name=None):
        self.ensure_one()
        if not self.env['hr.attendance.task'].search([('name', '=', task_name), ('id', '=', task_id)]):
            return {'warning': _('Wrong Task')}

        if self.env['res.users'].browse(SUPERUSER_ID).has_group(
                'hr_attendance.group_hr_attendance_use_pin'):
            if entered_pin != self.pin:
                return {'warning': _('Wrong PIN')}
        return self.with_context(new_task_id=task_id).attendance_action(next_action)
