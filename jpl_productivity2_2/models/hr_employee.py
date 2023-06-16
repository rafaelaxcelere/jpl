# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant JPLEAN")

    code_plant = fields.Char('Code Plant JPLEAN')

    def _compute_plant(self, code_plant):
        return self.env['jpl_prod.plant_table'].search([
            ('code_plant', '=', code_plant)
        ], limit=1)

    @api.model
    def create(self, values):
        if values.get('work_location', False):
            plant_id = self._compute_plant(values.get('code_plant'))
            values.update({'plant_id': plant_id.id})
        elif values.get('plant_id', False):
            values.update({'work_location': self._compute_plant(values.get('code_plant')).display_name})
        return super(HrEmployee, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('work_location', False):
            plant_id = self._compute_plant( values.get('code_plant'))
            values.update({'plant_id': plant_id.id})

        elif values.get('plant_id', False):
            values.update({'work_location': self._compute_plant(values.get('code_plant')).display_name})
        return super(HrEmployee, self).write(values)

    employee_category = fields.Many2one('jpl_prod.employee_category',  string="Categoria JPLEAN")

    employee_status = fields.Many2one('jpl_prod.employee_status', string="Estatus JPLEAN")

    mon_hour_contract = fields.Float(string='H.Contrato Lunes', store=True, default=0)
    tue_hour_contract = fields.Float(string='H.Contrato Martes', store=True, default=0)
    wed_hour_contract = fields.Float(string='H.Contrato Miercoles', store=True, default=0)
    thu_hour_contract = fields.Float(string='H.Contrato Jueves', store=True, default=0)
    fri_hour_contract = fields.Float(string='H.Contrato Viernes', store=True, default=0)
    sat_hour_contract = fields.Float(string='H.Contrato Sabado', store=True, default=0)
    sun_hour_contract = fields.Float(string='H.Contrato Domingo', store=True, default=0)


class Employee_Category(models.Model):
    _name = 'jpl_prod.employee_category'

    name = fields.Text('Nombre Categoria Empleado', required=True, store=True)
    description = fields.Text(default='---', store=True)
    active = fields.Boolean('Active', default=True)

class Employee_Status(models.Model):
    _name = 'jpl_prod.employee_status'

    name = fields.Text('Nombre Estatus Empleado', required=True, store=True)
    description = fields.Text(default='---', store=True)
    active = fields.Boolean('Active', default=True)

class Cost_Table(models.Model):
    _name = 'jpl_prod.cost_table'

    id_plant = fields.Many2one('jpl_prod.plant_table', ondelete='set null', string="Related Plant", index=False, required=True)

    id_category_employee = fields.Many2one('jpl_prod.employee_category', ondelete='set null', string="Categoria Empleado", index=False,
                               required=True)
    id_status_employee = fields.Many2one('jpl_prod.employee_status', ondelete='set null',
                                           string="Estatus Empleado", index=False,
                                           required=True)

    month = fields.Selection([(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                              (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                              (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'), ],
                             string='Month', required=True, index=True)

    year = fields.Selection([(2019, '2019'), (2020, '2020'), (2021, '2021'), (2022, '2022'),
                              (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'),
                              (2027, '2027'), (2028, '2028'), (2029, '2029'), (2030, '2030'), ],
                             string='Year', required=True, index=True)

    cost = fields.Float('Cost €/h', Ondelete='set null', required=True)
    active = fields.Boolean('Active', default=True)

    #@api.constrains('year')
    #def check_unique_cost(self):
    #    for rec in self:
    #        if self.search([('year', '=', rec.year)]):
    #            raise ValidationError(('El registro para esta fecha ya ha sido realizado anteriromente. No pueden existir dos registros para el mismo dia.'))

