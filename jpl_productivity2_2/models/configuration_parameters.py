# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

@api.model
def _tz_get(self):
    # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
    return [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


# Criterios de agrupacion jerarquica
class Area(models.Model):
    _name = 'jpl_prod.area_table'

    name = fields.Text('Area Name', required=True)
    responsable = fields.Many2one('res.users', required=True)
    related_division = fields.One2many('jpl_prod.division_table', 'related_area')
    active = fields.Boolean('Active', default=True)


class Division(models.Model):
    _name = 'jpl_prod.division_table'

    name = fields.Text('Division Name', required=True)
    responsable = fields.Many2one('res.users', required=True)
    related_area = fields.Many2one('jpl_prod.area_table', required=True)
    related_center = fields.One2many('jpl_prod.center_table', 'related_division')
    active = fields.Boolean('Active', default=True)


class Center(models.Model):
    _name = 'jpl_prod.center_table'

    name = fields.Text('Center Name', required=True)
    responsable = fields.Many2one('res.users', required=True)
    related_division = fields.Many2one('jpl_prod.division_table', required=True)
    related_plant = fields.One2many('jpl_prod.plant_table', 'related_center')
    active = fields.Boolean('Active', default=True)


class Plant(models.Model):
    _name = 'jpl_prod.plant_table'

    name = fields.Text('Plant Name', required=True)
    code_plant = fields.Char('Plant Code', required=True)
    responsable = fields.Many2one('res.users', required=True)
    related_center = fields.Many2one('jpl_prod.center_table', required=True)
    viewers = fields.Many2many('res.users', string="Manual viewers added")
    viewers2 = fields.Many2many('res.users', relation='jpl_prod_plant_table_res_users2_rel', string="Viewers", help='All users related to the plant ', compute='_compute_viewers2', store=True)
    cost = fields.Float('Cost €/h', Ondelete='set null', required=True)
    gm_objective = fields.Float('Objetivo Margen Bruto %', ondelete='set null', default=7.00, required=True)
    oee_objective = fields.Float('Objetivo OEE %', ondelete='set null', default=65.00, required=True)
    oee_limit = fields.Float('Limite OEE %', ondelete='set null', default=50.00, required=True)
    start_day_6am = fields.Boolean('Dia Imputacion Si=dia en curso; No=dia siguiente', required=True, default=True)
    start_day_hour = fields.Integer('Hora Inicio Jornada Laboral', default=6, required=True, store=True)
    start_day_minute = fields.Integer('Minutos Inicio Jornada Laboral', default=0, required=True, store=True)
    disp_objective = fields.Float('Objetivo DISP %', ondelete='set null', default=85.00, required=True)
    tz = fields.Selection(_tz_get, string='Zona horaria',
                          default='Europe/Madrid')
    # Related activities
    related_processes = fields.One2many('jpl_prod.process_table', 'related_plant')
    related_processesperhours = fields.One2many('jpl_prod.hourprocess_table', 'related_plant')
    related_inefficiences = fields.One2many('jpl_prod.inef_table', 'related_plant')
    active = fields.Boolean('Active', default=True)
    active_emails = fields.Boolean('Email')

    @api.constrains('start_day_hour')
    def check_correct_hour(self):
        for rec in self:
            if isinstance(rec.start_day_hour, int):
                if rec.start_day_hour > 23:
                    raise ValidationError(_('La hora de inicio ha de estar comprendida entre las 0h y las 23h'))
            else:
                raise ValidationError(_('La hora ha de ser un número entero. Sin decimales'))

    @api.constrains('start_day_minute')
    def check_correct_minute(self):
        for rec in self:
            if isinstance(rec.start_day_minute, int):
                if rec.start_day_minute > 59:
                    raise ValidationError(_('Los minutos de inicio han de estar comprendidos entre las 0 y 59'))
            else:
                raise ValidationError(_('Los minutos han de ser un número entero. Sin decimales'))


    @api.constrains('code_plant')
    def check_unique_code_plant(self):
        for rec in self:
            if self.search([('code_plant', '=', rec.code_plant), ('id', '!=', rec.id)]):
                raise ValidationError(_('No se pueden crear dos plantas con el mismo "PLANT CODE".'))

    @api.constrains('name')
    def check_unique_name_plant(self):
        for rec in self:
            if self.search([('name', '=', rec.name), ('id', '!=', rec.id)]):
                raise ValidationError(_('El nombre de la planta ya a sido utilizado. No puede haber dos plantas con el mismo nombre.'))

    @api.multi
    @api.depends('viewers', 'responsable', 'related_center.responsable', 'related_center.related_division.responsable',
                 'related_center.related_division.related_area.responsable')
    def _compute_viewers2(self):
        for plant in self:
            areaViewer = plant.related_center.related_division.related_area.responsable
            divisionViewer = plant.related_center.related_division.responsable
            centerViewer = plant.related_center.responsable
            plantViewer = plant.responsable

            plant.viewers2 = areaViewer | divisionViewer | centerViewer | plantViewer | plant.viewers
