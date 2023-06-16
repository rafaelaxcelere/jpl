# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

    #Processes

class ProcessCategoryTable(models.Model):
    _name = 'jpl_prod.process_category_table'

    name = fields.Text(required=True)
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)

class ProcessSubCategoryTable(models.Model):
    _name = 'jpl_prod.process_sub_category_table'

    name = fields.Text(required=True)
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)

class ProcessTable(models.Model):
    _name = 'jpl_prod.process_table'

    name = fields.Text('Process', required=True)
    related_plant = fields.Many2one('jpl_prod.plant_table', ondelete='set null', string="Related Plant", index=False, required=True)
    id_cat = fields.Many2one('jpl_prod.process_category_table', ondelete='set null', string="Categoria",
                             index=False, required=True)
    id_sub_cat = fields.Many2one('jpl_prod.process_sub_category_table', ondelete='set null', string="Subcategoria",
                             index=False)
    effxprocess_objective = fields.Float('Objetivo Eff %', ondelete='set null', default=80.00, required=True)
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)
    related_tasks = fields.One2many('jpl_prod.task_table', 'id_related_process')
    related_productivity_wastes = fields.One2many('jpl_prod.productivity_waste_table', 'id_process')
    ref_1 = fields.Text('Referencia 1')
    ref_2 = fields.Text('Referencia 2')

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}

        new_name = (self.name + ' (copy)') if self.name else ''
        default.update({
            'name': new_name,
        })
        res = super(ProcessTable, self).copy(default=default)

        dom_lost = [
            ('id_process', '=', self.id)
        ]
        lost_ids = self.env['jpl_prod.productivity_waste_table'].search(
            dom_lost)
        dom_task = [
            ('id_related_process', '=', self.id)
        ]
        task_ids = self.env['jpl_prod.task_table'].search(dom_task)
        for lost in lost_ids:
            lost.copy(
                {
                    'id_process': res.id
                }
            )
        for task in task_ids:
            task.copy(
                {
                    'id_related_process': res.id
                }
            )
        return res

    @api.constrains('name')
    def check_unique_name_process(self):
        for rec in self:
            if self.search(
                    [('related_plant', '=', rec.related_plant.id), ('name', '=', rec.name), ('id', '!=', rec.id)]):
                raise ValidationError(_(
                    'No puede haber dos procesos con el mismo nombre para una misma planta.'))

    @api.multi
    def toggle_active(self):
        for record in self:
            dom_lost = [
                ('id_process', '=', record.id),
                ('active', '=', record.active)
            ]
            lost_ids = self.env['jpl_prod.productivity_waste_table'].search(
                dom_lost)
            lost_ids.write(dict(active=not record.active))
            dom_task = [
                ('id_related_process', '=', record.id),
                ('active', '=', record.active)
            ]
            task_ids = self.env['jpl_prod.task_table'].search(dom_task)
            task_ids.write(dict(active=not record.active))
            record.active = not record.active

class TaskTable(models.Model):
    _name = 'jpl_prod.task_table'

    name = fields.Text('Task', required=True)
    standard_time = fields.Float('Standard Time (Seconds/unit)', required=True)
    elementary_unit = fields.Text('Elementary Unit', required=True)
    id_related_process = fields.Many2one('jpl_prod.process_table', ondelete='set null', string="Related_Process",
                              index=False, required=True)
    id_related_plant = fields.Many2one(related='id_related_process.related_plant', required=True, readonly=True, index=False)
    price = fields.Float('PVP (€/unit)', required=True, digits=(12, 4))
    description = fields.Text(required=False)
    active = fields.Boolean('Active', default=True)
    form_order = fields.Integer(string='Orden de formulario', store=True, default=0)

    @api.constrains('name')
    def check_unique_name_task(self):
        for rec in self:
            if self.search([('id_related_plant', '=', rec.id_related_plant.id),
                            ('id_related_process', '=', rec.id_related_process.id), ('name', '=', rec.name),
                            ('id', '!=', rec.id)]):
                raise ValidationError(_(
                    'No puede haber dos tareas con el mismo nombre para un mismo proceso y una misma planta.'))


class ProductivityWasteTable(models.Model):
    _name = 'jpl_prod.productivity_waste_table'

    name = fields.Text('Productivity Waste', required=True)
    waste_standard_time = fields.Float('Waste Standard Time (Seconds/time)', required=True)
    elementary_unit = fields.Text('Elementary Unit', required=True)
    id_process = fields.Many2one('jpl_prod.process_table', ondelete='set null', string="Related_Process", index=False, required=True)
    id_related_plant = fields.Many2one(related='id_process.related_plant', required=True, readonly=True)
    price = fields.Float('PVP (€/unit)', required=True, digits=(12, 4))
    description = fields.Text(required=False)
    active = fields.Boolean('Active', default=True)

    @api.constrains('name')
    def check_unique_name_task(self):
        for rec in self:
            if self.search([('id_related_plant', '=', rec.id_related_plant.id),
                            ('id_process', '=', rec.id_process.id), ('name', '=', rec.name),
                            ('id', '!=', rec.id)]):
                raise ValidationError(_(
                    'No puede haber dos perdidas productivas con el mismo nombre para un mismo proceso y una misma planta.'))


class InefficienciesCategoryTable(models.Model):
    _name = 'jpl_prod.inef_category_table'

    name = fields.Text(required=True)
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)


class InefficienciesTable(models.Model):
    _name = 'jpl_prod.inef_table'

    name = fields.Text('Inefficiency Name', required=True)
    related_plant = fields.Many2one('jpl_prod.plant_table', ondelete='set null', string="Related Plant", index=False,
                                    required=True)
    id_cat = fields.Many2one('jpl_prod.process_category_table', ondelete='set null', string="Category",
                             index=False, required=True)
    id_sub_cat = fields.Many2one('jpl_prod.process_sub_category_table', ondelete='set null', string="Subcategoria",
                                 index=False)
    price = fields.Float('PVP (€/unit)', required=True, digits=(12, 4))
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)


    #facturación por horas
class ProcesosHorasTable(models.Model):
    _name = 'jpl_prod.hourprocess_table'

    name = fields.Text('Houre Process Name', required=True)
    related_plant = fields.Many2one('jpl_prod.plant_table', ondelete='set null', string="Related Plant", index=False,
                                    required=True)
    price = fields.Float('PVP (€/unit)', required=True)
    id_cat = fields.Many2one('jpl_prod.process_category_table', ondelete='set null', string="Category",
                             index=False, required=True)
    id_sub_cat = fields.Many2one('jpl_prod.process_sub_category_table', ondelete='set null', string="Subcategoria",
                                 index=False)
    description = fields.Text(required=True)
    active = fields.Boolean('Active', default=True)


