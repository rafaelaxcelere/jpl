# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.tools.sql import drop_view_if_exists
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import pytz


class JPLAlertLogs(models.Model):
    _name = 'jpl.alert.logs'

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', string='Employee')
    worked_hours = fields.Char(string="Worked hours")
    related_plant = fields.Many2one('jpl_prod.plant_table', string='Plant')
