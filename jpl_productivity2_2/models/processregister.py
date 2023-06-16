# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import dateutil.parser
from odoo.tools.sql import drop_view_if_exists

    #Process Register

class TaskRegisterTable(models.Model):
    _name = 'jpl_prod.task_register_table'

    #variables de identificación

    id_task = fields.Many2one('jpl_prod.task_table', ondelete='set null', string="Tarea",
                              index=False, store=True)
    order = fields.Integer(related='id_task.form_order', string='nº', index=False, readonly=True, store=True)
    reg_id = fields.Many2one('jpl_prod.reg_table', ondelete='cascade', string="Registero", index=False, store=True)
    related_process = fields.Many2one(related='id_task.id_related_process', string='Proceso Relacionado', store=True, readonly=True)

    @api.depends('reg_id.date')
    def _computed_price(self):
        for record in self:
            record.price = record.id_task.price

    price = fields.Float(default=0.00, compute=_computed_price, store=True, readonly=True)
    id_cat = fields.Many2one(related='id_task.id_related_process.id_cat', string='Categoria', store=True, readonly=True)
    id_sub_cat = fields.Many2one(related='id_task.id_related_process.id_sub_cat', string='Subcategoria', store=True, readonly=True)

    #solo para visualización
    related_process_on_task_view = fields.Text(string="Related Process", index=False, required=True)
    elementary_unit_on_task_view = fields.Text(string="Elementary Unit", index=False, required=True)

    #unidades
    @api.onchange('id_task')
    def _units_registered(self):
        for record in self:
            possible_registers = self.env['jpl_prod.units_employee'].sudo().search(
                [('start_date', '=', record.reg_id.date), ('type_task', '=', "Tarea"), ('id_process', '=', record.related_process.id), ('id_task', '=', record.id_task.id)])
            record.units = sum(possible_registers.mapped('units'))
            record.scrap_units = sum(possible_registers.mapped('scrap_units'))

    units = fields.Float('Units', required=True, default=0, store=True)
    scrap_units = fields.Float('Scrap Units', required=True, default=0, store=True)

    #Calculo de tiempos


    @api.depends('units')
    def _compute_standard_time(self):
        for record in self:
            record.ef_op_time = record.units * record.id_task.standard_time / 3600

    ef_op_time = fields.Float(compute='_compute_standard_time', store=True)

    @api.depends('scrap_units')
    def _compute_scrap_wasted_time(self):
        for record in self:
            record.scrap_wasted_time = record.scrap_units * record.id_task.standard_time / 3600

    scrap_wasted_time = fields.Float(compute='_compute_scrap_wasted_time', store=True, default=0)

    @api.depends('ef_op_time', 'scrap_wasted_time')
    def _compute_add_val_op_time(self):
        for record in self:
            record.add_val_op_time = record.ef_op_time - record.scrap_wasted_time

    add_val_op_time = fields.Float(compute='_compute_add_val_op_time', store=True, default=0)

    billing = fields.Float(compute='_computed_billing', store=True, default=0.0)

    @api.depends('units')
    def _computed_billing(self):
        for record in self:
            record.billing = record.units * record.price


class ProdWasteRegisterTable(models.Model):
    _name = 'jpl_prod.prod_waste_reg_table'

    # variables de identificación
    id_prod_waste = fields.Many2one('jpl_prod.productivity_waste_table', ondelete='set null',
                              string="Productivity Waste", index=False)
    reg_id = fields.Many2one('jpl_prod.reg_table', ondelete='cascade', string="Register", index=False)
    related_process = fields.Many2one(related='id_prod_waste.id_process', string='Proceso Relacionado', store=True,
                                      readonly=True)
    related_process_on_task = fields.Text(ondelete='set null', string="Related Process", index=False, required=True)

    # unidades
    @api.onchange('prod_waste')
    def _units_waste_registered(self):
        for record in self:
            possible_registers = self.env['jpl_prod.units_employee'].sudo().search(
                [('start_date', '=', record.reg_id.date), ('type_task', '=', "Perdida"),
                 ('id_process', '=', record.related_process.id), ('id_waste', '=', record.id_prod_waste.id)])
            record.units = sum(possible_registers.mapped('units'))

    units = fields.Integer('Units', required=True, default=0)

    @api.depends('reg_id.date')
    def _computed_price(self):
        for record in self:
            record.price = record.id_prod_waste.price

    price = fields.Float(default=0.00, compute=_computed_price, store=True, readonly=True)
    id_cat = fields.Many2one(related='id_prod_waste.id_process.id_cat', string='Categoria', store=True, readonly=True)
    id_sub_cat = fields.Many2one(related='id_prod_waste.id_process.id_sub_cat', string='Subcategoria', store=True,
                                 readonly=True)

    # Calculo de tiempos
    prod_wasted_time = fields.Float(compute='_computed_prod_wasted_time', store=True, default=0)

    @api.depends('units')
    def _computed_prod_wasted_time(self):
        for record in self:
            record.prod_wasted_time = record.units * record.id_prod_waste.waste_standard_time / 3600

    billing = fields.Float(compute='_computed_billing', store=True)

    @api.depends('units')
    def _computed_billing(self):
        for record in self:
            record.billing = record.units * record.price


class ProcessRegisterTable(models.Model):
    _name = 'jpl_prod.process_reg_table'

    # variables de identificación
    id_process = fields.Many2one('jpl_prod.process_table', ondelete='set null', string="Process", index=False)
    reg_id = fields.Many2one('jpl_prod.reg_table', ondelete='cascade', string="Register", index=False)
    date = fields.Date(related='reg_id.date', readonly=True, required=False, index=True, store=True)
    id_area = fields.Many2one(related='id_process.related_plant.related_center.related_division.related_area', string='Area', store=True, readonly=True,  ondelete='set null')
    id_division = fields.Many2one(related='id_process.related_plant.related_center.related_division', string='Division', store=True, readonly=True,  ondelete='set null')
    id_center = fields.Many2one(related='id_process.related_plant.related_center', string='Center', store=True, readonly=True,  ondelete='set null')
    id_plant = fields.Many2one(related='id_process.related_plant', string='Plant', store=True, readonly=True,  ondelete='set null')
    id_category = fields.Many2one(related='id_process.id_cat', string='Category', store=True, readonly=True,  ondelete='set null')
    id_subcategory = fields.Many2one(related='id_process.id_sub_cat', string='Category', store=True, readonly=True,
                                  ondelete='set null')
    ref_1 = fields.Text(related='id_process.ref_1', string='Referencia 1', store=True)
    ref_2 = fields.Text(related='id_process.ref_2', string='Referencia 2', store=True)

    perf = fields.Float(string="% Perf")
    qlty = fields.Float(string="% Qlty")
    eff_x_process = fields.Float(string="% Efficiency x process")

    @api.depends('reg_id.date')
    def _computed_perf_obj(self):
        for record in self:
            record.effxprocess_objective = record.id_process.effxprocess_objective

    effxprocess_objective = fields.Float(compute='_computed_perf_obj', default=80, group_operator='avg',
                                 string='Objetivo EFF x proceso (%)', store=True,
                                 readonly=True, required=True)
    fulfillment_perf = fields.Float(string="% Cumplimiento Eff")
    #productivity_process = fields.Float(string="Uds/h")
    gm_process = fields.Float(string="%Margen Proceso")

    # time
    @api.onchange('id_plant', 'id_process')
    def _process_attendance_op_time(self):
        for record in self:
            possible_registers = self.env['hr.attendance'].sudo().search(
                [('start_date', '=', record.reg_id.date), ('related_plant', '=', record.id_plant.id),
                 ('type', '=', "process"), ('id_activity', '=', record.id_process.id), ('check_out', '!=', False)])
            record.op_time = sum(possible_registers.mapped('worked_hours'))

    op_time = fields.Float(required=True, default=0.0, readonly=False)

    @api.depends('id_process', 'reg_id')
    def _compute_possible_prod_waste_reg_table_ids(self):
        for record in self:
            record.possible_prod_waste_reg_table_ids = self.env['jpl_prod.prod_waste_reg_table'].search(
                [('reg_id', '=', record.reg_id.id), ('id_prod_waste.id_process', '=', record.id_process.id)])

    possible_prod_waste_reg_table_ids = fields.Many2many(
        'jpl_prod.prod_waste_reg_table', compute=_compute_possible_prod_waste_reg_table_ids, store=True)

    @api.depends('possible_prod_waste_reg_table_ids.prod_wasted_time')
    def _productivity_waste_time(self):
        for record in self:
            record.productivity_waste_time = sum(record.possible_prod_waste_reg_table_ids.mapped('prod_wasted_time'))

    productivity_waste_time = fields.Float(compute=_productivity_waste_time, store=True, required=True, default=0.0, readonly=True)

    @api.depends('id_process', 'reg_id')
    def _compute_possible_task_register_table_ids(self):
        for record in self:
            record.possible_task_register_table_ids = self.env['jpl_prod.task_register_table'].search(
                [('reg_id', '=', record.reg_id.id),
                 ('id_task.id_related_process', '=', record.id_process.id)]
            )

    possible_task_register_table_ids = fields.Many2many(
        comodel_name="jpl_prod.task_register_table", compute=_compute_possible_task_register_table_ids, store=True)

    @api.depends('possible_task_register_table_ids.ef_op_time', 'possible_task_register_table_ids.ef_op_time')
    def _computed_effective_time(self):
        for record in self:
            record.standard_time_in_process = sum(record.possible_task_register_table_ids.mapped('ef_op_time'))
     #       record.units_of_process = sum(record.possible_task_register_table_ids.mapped('units'))

    standard_time_in_process = fields.Float(compute='_computed_effective_time', required=True, store=True, default=0.00)
    #units_of_process = fields.Float(compute='_computed_effective_time', string="Unidades Totales de proceso", required=True, default=0.0,
    #                                ondelete='set null', store=True)

    @api.depends('op_time', 'productivity_waste_time', 'standard_time_in_process')
    def _compute_slow_rhythm(self):
        for record in self:
            record.slow_rhythm_time = record.op_time - record.productivity_waste_time - record.standard_time_in_process

    slow_rhythm_time = fields.Float(compute=_compute_slow_rhythm, store=True, default=0.0, readonly=True)

    @api.depends('possible_task_register_table_ids.add_val_op_time')
    def _computed_add_val_time_in_process(self):
        for record in self:
            record.add_val_time_in_process = sum(record.possible_task_register_table_ids.mapped('add_val_op_time'))

    add_val_time_in_process = fields.Float(compute='_computed_add_val_time_in_process', required=True, store=True,
                                           default=0.00)

    @api.depends('standard_time_in_process', 'add_val_time_in_process')
    def _compute_scrap_time(self):
        for record in self:
            record.scrap_time = record.standard_time_in_process - record.add_val_time_in_process

    scrap_time = fields.Float(compute=_compute_scrap_time, store=True, default=0.0, readonly=True)

    # Econmical parameters

    @api.depends('op_time')
    def _computed_cost(self):
        for record in self:
            op_time_control = 0
            possible_registers = self.env['hr.attendance'].search(
                [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                 ('type', '=', "process"), ('id_activity', '=', record.id_process.id), ('check_out', '!=', False)])
            for p_r in possible_registers:
                op_time_control += p_r.worked_hours
            record.op_time_c = op_time_control

            if record.op_time == op_time_control:
                possible_registers = self.env['hr.attendance'].search(
                    [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                     ('type', '=', "process"), ('id_activity', '=', record.id_process.id), ('check_out', '!=', False)])
                record.cost_process = sum(possible_registers.mapped('activity_cost'))
                record.cost_calculated_by_attendance = True

            else:
                record.cost_process = record.op_time * record.id_plant.cost
                record.cost_calculated_by_attendance = False

    op_time_c = fields.Float(compute=_computed_cost, store=True)
    cost_process = fields.Float(default=0.00, compute=_computed_cost, store=True, required=True)
    cost_calculated_by_attendance = fields.Boolean(string='Cost Calculated by attendance', store=True, compute=_computed_cost, required=True)

    @api.depends('possible_task_register_table_ids.billing', 'possible_prod_waste_reg_table_ids.billing')
    def _computed_billing(self):
        for record in self:
            total_billing_process_tasks = sum(record.possible_task_register_table_ids.mapped('billing'))
            total_billing_process_prod_wast = sum(record.possible_prod_waste_reg_table_ids.mapped('billing'))
            record.billing_process = total_billing_process_tasks + total_billing_process_prod_wast

    billing_process = fields.Float(compute='_computed_billing', required=True, store=True, default=0.00,)

    # Visualizacion Porcentajes

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(ProcessRegisterTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                    orderby=orderby, lazy=lazy)
        for line in res:
            if 'op_time' in fields and 'standard_time_in_process' in fields:
                if line['op_time'] in (0, None):
                    line['perf'] = 0
                else:
                    if line['standard_time_in_process'] in (0, None):
                        line['perf'] = 1.00
                    else:
                        line['perf'] = line['standard_time_in_process'] / line['op_time'] * 100
            else:
                if 'perf' in fields:
                    fields.remove('perf')

            if 'add_val_time_in_process' in fields and 'standard_time_in_process' in fields:
                if line['standard_time_in_process'] in (0, None):
                    line['qlty'] = 0
                else:
                    line['qlty'] = line['add_val_time_in_process'] / line['standard_time_in_process'] * 100

            else:
                if 'qlty' in fields:
                    fields.remove('qlty')

            if 'add_val_time_in_process' in fields and 'op_time' in fields:
                if line['op_time'] in (0, None):
                    line['Eff_x_process'] = 0
                else:
                    if line['add_val_time_in_process'] in (0, None):
                        line['Eff_x_process'] = 1.00
                    else:
                        line['Eff_x_process'] = line['add_val_time_in_process'] / line['op_time'] * 100
            else:
                if 'Eff_x_process' in fields:
                    fields.remove('Eff_x_process')

            if 'Eff_x_process' in fields and 'effxprocess_objective' in fields:
                if line['Eff_x_process'] in (0, None):
                    line['fulfillment_perf'] = 0
                else:
                    line['fulfillment_perf'] = line['Eff_x_process']-line['effxprocess_objective']
            else:
                if 'fulfillment_perf' in fields:
                    fields.remove('fulfillment_perf')

            if 'cost_process' in fields and 'billing_process' in fields:
                if line['billing_process']*line['cost_process'] in (0, None):
                    line['gm_process'] = 0
                else:
                    line['gm_process'] = ((line['billing_process']-line['cost_process'])/line['billing_process'])*100
            else:
                if 'gm_process' in fields:
                    fields.remove('gm_process')

        return res


class HourProcessRegisterTable(models.Model):
    _name = 'jpl_prod.hourprocess_reg_table'

    # variables de identificación
    id_processxhours = fields.Many2one('jpl_prod.hourprocess_table', ondelete='set null', string="Hour Process", index=False)

    id_area = fields.Many2one(related='id_processxhours.related_plant.related_center.related_division.related_area',
                              string='Area', store=True, readonly=True, ondelete='set null')
    id_division = fields.Many2one(related='id_processxhours.related_plant.related_center.related_division', string='Division',
                                  store=True, readonly=True, ondelete='set null')
    id_center = fields.Many2one(related='id_processxhours.related_plant.related_center', string='Center', store=True,
                                readonly=True, ondelete='set null')
    id_plant = fields.Many2one(related='id_processxhours.related_plant', string='Plant', store=True, readonly=True,
                               ondelete='set null')
    id_category = fields.Many2one(related='id_processxhours.id_cat', string='Category', store=True, readonly=True,
                                  ondelete='set null')
    id_subcategory = fields.Many2one(related='id_processxhours.id_sub_cat', string='Category', store=True, readonly=True,
                                  ondelete='set null')
    reg_id = fields.Many2one('jpl_prod.reg_table', ondelete='cascade', string="Register", index=False)

    # tiempo
    date = fields.Date(related='reg_id.date', required=False, index=True, store=True, readonly=True)

    # time
    @api.onchange('id_plant', 'id_processxhours', 'date')
    def _hour_process_attendance_op_time(self):
        for record in self:
            possible_registers = self.env['hr.attendance'].sudo().search(
                [('start_date', '=', record.reg_id.date), ('related_plant', '=', record.id_plant.id), ('type', '=', "hours_process"),
                 ('id_activity', '=', record.id_processxhours.id), ('check_out', '!=', False)])
            record.op_time = sum(possible_registers.mapped('worked_hours'))

    op_time = fields.Float(required=True, default=0.0, readonly=False)

    # Econmical parameters
    @api.depends('op_time')
    def _computed_cost(self):
        for record in self:
            op_time_control = 0
            possible_registers = self.env['hr.attendance'].search(
                [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                 ('type', '=', "hours_process"),
                 ('id_activity', '=', record.id_processxhours.id), ('check_out', '!=', False)])
            for p_r in possible_registers:
                op_time_control += p_r.worked_hours
            record.op_time_c = op_time_control

            if record.op_time == op_time_control:
                possible_registers = self.env['hr.attendance'].search(
                    [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                     ('type', '=', "hours_process"),
                     ('id_activity', '=', record.id_processxhours.id), ('check_out', '!=', False)])
                record.cost_hours = sum(possible_registers.mapped('activity_cost'))
                record.cost_calculated_by_attendance = True

            else:
                record.cost_hours = record.op_time * record.id_plant.cost
                record.cost_calculated_by_attendance = False

    cost_hours = fields.Float(default=0.00, compute=_computed_cost, store=True, required=True)
    op_time_c = fields.Float(compute=_computed_cost, store=True)
    cost_calculated_by_attendance = fields.Boolean(string='Cost Calculated by attendance', store=True,
                                                   compute=_computed_cost, required=True)

    @api.depends('reg_id.date')
    def _computed_price(self):
        for record in self:
            record.price = record.id_processxhours.price

    price = fields.Float(default=0.00, compute=_computed_price, store=True, readonly=True)

    @api.depends('op_time')
    def _computed_billing(self):
        for record in self:
            record.billing_hours = record.op_time * record.price

    billing_hours = fields.Float(default=0.00, compute=_computed_billing, store=True, required=True)





class InefficienciesRegisterTable(models.Model):
    _name = 'jpl_prod.inef_reg_table'

    id_inef = fields.Many2one('jpl_prod.inef_table', ondelete='set null', string="Not productive time",
                              index=False)

    id_area = fields.Many2one(related='id_inef.related_plant.related_center.related_division.related_area',
                              string='Area', store=True, readonly=True, ondelete='set null')
    id_division = fields.Many2one(related='id_inef.related_plant.related_center.related_division', string='Division',
                                  store=True, readonly=True, ondelete='set null')
    id_center = fields.Many2one(related='id_inef.related_plant.related_center', string='Center', store=True,
                                readonly=True, ondelete='set null')
    id_plant = fields.Many2one(related='id_inef.related_plant', string='Plant', store=True, readonly=True,
                               ondelete='set null')
    id_category = fields.Many2one(related='id_inef.id_cat', string='Category', store=True, readonly=True,
                                  ondelete='set null')
    id_subcategory = fields.Many2one(related='id_inef.id_sub_cat', string='Subcategory', store=True, readonly=True,
                                  ondelete='set null')
    reg_id = fields.Many2one('jpl_prod.reg_table', ondelete='cascade', string="Register", index=False)

    date = fields.Date(related='reg_id.date', required=False, index=True, store=True)

    @api.onchange('id_plant', 'id_inef')
    def _inef_attendance_dest_time(self):
        for record in self:
            possible_registers = self.env['hr.attendance'].sudo().search(
                [('start_date', '=', record.reg_id.date), ('related_plant', '=', record.id_plant.id), ('type', '=', "inefficiency"),
                 ('id_activity', '=', record.id_inef.id), ('check_out', '!=', False)])
            record.dest_time = sum(possible_registers.mapped('worked_hours'))

    dest_time = fields.Float(required=True, default=0.00, store=True)

    comments = fields.Text(required=False, store=True)

    # Econmical parameters
    @api.depends('dest_time')
    def _computed_cost(self):
        for record in self:
            op_time_control = 0
            possible_registers = self.env['hr.attendance'].search(
                [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                 ('type', '=', "inefficiency"),
                 ('id_activity', '=', record.id_inef.id), ('check_out', '!=', False)])
            for p_r in possible_registers:
                op_time_control += p_r.worked_hours
            record.op_time_c = op_time_control

            if record.dest_time == op_time_control:
                possible_registers = self.env['hr.attendance'].search(
                    [('start_date', '=', record.date), ('related_plant', '=', record.id_plant.id),
                     ('type', '=', "inefficiency"),
                     ('id_activity', '=', record.id_inef.id), ('check_out', '!=', False)])
                record.cost_hours = sum(possible_registers.mapped('activity_cost'))
                record.cost_calculated_by_attendance = True

            else:
                record.cost_hours = record.dest_time * record.id_plant.cost
                record.cost_calculated_by_attendance = False

    cost_hours = fields.Float(default=0.00, compute=_computed_cost, store=True, required=True)
    op_time_c = fields.Float(compute=_computed_cost, store=True)
    cost_calculated_by_attendance = fields.Boolean(string='Cost Calculated by attendance', store=True,
                                                   compute=_computed_cost, required=True)

    @api.depends('reg_id.date')
    def _computed_price(self):
        for record in self:
            record.price = record.id_inef.price

    price = fields.Float(default=0.00, compute=_computed_price, store=True, readonly=True)

    @api.depends('dest_time')
    def _computed_billing(self):
        for record in self:
            record.billing_hours = record.dest_time * record.price

    billing_hours = fields.Float(default=0.00, compute=_computed_billing, store=True, required=True,)



class EfficiencySlqTable(models.Model):
    _name = 'jpl_prod.efficiency_sql_table'
    _auto = False

    id = fields.Integer(readonly=True)
    date = fields.Date(readonly=True, string="Fecha")
    id_area = fields.Many2one(comodel_name='jpl_prod.area_table', string="Area", readonly=True)
    id_division = fields.Many2one(comodel_name='jpl_prod.division_table', string="Division", readonly=True)
    id_center = fields.Many2one(comodel_name='jpl_prod.center_table', string="Centro", readonly=True)
    id_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
    id_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Categoria", readonly=True)
    id_sub_cat = fields.Many2one(comodel_name='jpl_prod.process_sub_category_table', string="Subcategoria", readonly=True)
    id_process = fields.Many2one(comodel_name='jpl_prod.process_table', string="Proceso", readonly=True)
    concepto = fields.Char(readonly=True, string="Concepto")
    name = fields.Char(readonly=True, string="Nombre")
    op_time = fields.Float(readonly=True, string="H.Productivas")
    waste_time = fields.Float(readonly=True, string="H.Per.Prod")
    std_time = fields.Float(readonly=True, string="H.STD")
    scarp_time = fields.Float(readonly=True, string="H.Per.Cal")
    added_val_time = fields.Float(readonly=True, string="H.Valor")
    uds = fields.Float(string="Unidades")
    perf = fields.Float(string="% Perf")
    qlty = fields.Float(string="% Qlty")
    eff_process = fields.Float(string="% Eficiencia")
    eff_process_obj = fields.Float(string='Ef. Obj (%)', group_operator='avg', readonly=True)
    fulfillment_perf = fields.Float(string="% Cumpl.Obj")
    uds_h = fields.Float(string="Uds/h")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_efficiency_sql_table')
        self._cr.execute("""CREATE VIEW jpl_prod_efficiency_sql_table AS(

        select
        (1000000000 + prt.id) as id,
        prt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        pt.id_cat as id_cat,
        pt.id_sub_cat as id_sub_cat,
        prt.id_process as id_process,
        concat('Procesos') as concepto,
        concat('Proceso') as name,
        prt.op_time as op_time,
        0 as waste_time,
        0 as std_time,
        0 as scarp_time,
        0 as added_val_time,
        0 as uds,
        prt.perf as perf,
        prt.qlty as qlty,
        prt.eff_x_process as eff_process,
        prt.effxprocess_objective as eff_process_obj,
        prt.fulfillment_perf as fulfillment_perf,
        prt.fulfillment_perf as uds_h
        from jpl_prod_process_reg_table prt
        inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
        union all
        select
        (2000000000 + trt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        pt.id_cat as id_cat,
        pt.id_sub_cat as id_sub_cat,
        trt.related_process as id_process,
        concat('Tareas') as concepto,
        tt.name as name,
        0 as op_time,
        0 as waste_time,
        trt.ef_op_time as std_time,
        trt.scrap_wasted_time as scarp_time,
        trt.add_val_op_time as added_val_time,
        (trt.units - trt.scrap_units) as uds,
        0 as perf,
        0 as qlty,
        0 as eff_process,
        pt.effxprocess_objective as eff_process_obj,
        0 as fulfillment_perf,
        0 as uds_h
        from jpl_prod_task_register_table trt
        inner join jpl_prod_reg_table rt on (trt.reg_id = rt.id)
        inner join jpl_prod_process_table pt on (trt.related_process = pt.id)
        inner join jpl_prod_task_table tt on (trt.id_task = tt.id)
        union all
        select
        (3000000000 + pwrt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        pt.id_cat as id_cat,
        pt.id_sub_cat as id_sub_cat,
        pwt.id_process as id_process,
        concat('Perdidas Productivas') as concepto,
        pwt.name as name,
        0 as op_time,
        pwrt.prod_wasted_time waste_time,
        0 as std_time,
        0 as scarp_time,
        0 as added_val_time,
        0 as uds,
        0 as perf,
        0 as qlty,
        0 as eff_process,
        pt.effxprocess_objective as eff_process_obj,
        0 as fulfillment_perf,
        0 as uds_h
        from jpl_prod_prod_waste_reg_table pwrt
        inner join jpl_prod_reg_table rt on (pwrt.reg_id = rt.id)
        inner join jpl_prod_productivity_waste_table pwt on (pwrt.id_prod_waste = pwt.id)
        inner join jpl_prod_process_table pt on (pwt.id_process = pt.id)
        union all
        select
        (4000000000 + prt.id) as id,
        prt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        pt.id_cat as id_cat,
        pt.id_sub_cat as id_sub_cat,
        prt.id_process as id_process,
        concat('Perdidas Productivas') as concepto,
        concat('Ritmo Lento') as name,
        0 as op_time,
        prt.slow_rhythm_time as waste_time,
        0 as std_time,
        0 as scarp_time,
        0 as added_val_time,
        0 as uds,
        0 as perf,
        0 as qlty,
        0 as eff_process,
        pt.effxprocess_objective as eff_process_obj,
        0 as fulfillment_perf,
        0 as uds_h
        from jpl_prod_process_reg_table prt
        inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
        order by id desc
        
          )""")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(EfficiencySlqTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                    orderby=orderby, lazy=lazy)
        for line in res:
            if 'op_time' in fields and 'std_time' in fields:
                if line['op_time'] in (0, None):
                    line['perf'] = 0
                else:
                    line['perf'] = (line['std_time'] / line['op_time']) * 100
            else:
                if 'perf' in fields:
                    fields.remove('perf')

            if 'added_val_time' in fields and 'std_time' in fields:
                if line['std_time'] in (0, None):
                    line['qlty'] = 0
                else:
                    line['qlty'] = line['added_val_time'] / line['std_time'] * 100
            else:
                if 'qlty' in fields:
                    fields.remove('qlty')

            if 'op_time' in fields and 'added_val_time' in fields:
                if line['op_time'] in (0, None):
                    line['eff_process'] = 0
                else:
                    line['eff_process'] = (line['added_val_time'] / line['op_time']) * 100
            else:
                if 'eff_process' in fields:
                    fields.remove('eff_process')

            if 'eff_process' in fields and 'eff_process_obj' in fields:
                if line['eff_process'] in (0, None):
                    line['fulfillment_perf'] = 0
                else:
                    line['fulfillment_perf'] = line['eff_process'] - line['eff_process_obj']
            else:
                if 'fulfillment_perf' in fields:
                    fields.remove('fulfillment_perf')

            if 'op_time' in fields and 'uds' in fields:
               if line['op_time'] in (0, None):
                   line['uds_h'] = 0
               else:
                   line['uds_h'] = line['uds']/line['op_time']
            else:
               if 'uds_h' in fields:
                   fields.remove('uds_h')

        return res

class WasteSlqTable(models.Model):
    _name = 'jpl_prod.waste_sql_table'
    _auto = False

    id = fields.Integer(readonly=True)
    date = fields.Date(readonly=True, string="Fecha")
    id_area = fields.Many2one(comodel_name='jpl_prod.area_table', string="Area", readonly=True)
    id_division = fields.Many2one(comodel_name='jpl_prod.division_table', string="Division", readonly=True)
    id_center = fields.Many2one(comodel_name='jpl_prod.center_table', string="Centro", readonly=True)
    id_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
    id_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Categoria", readonly=True)
    id_sub_cat = fields.Many2one(comodel_name='jpl_prod.process_sub_category_table', string="Subcategoria", readonly=True)
    concepto = fields.Char(readonly=True, string="Concepto")
    type = fields.Char(readonly=True, string="Tipo")
    name = fields.Char(readonly=True, string="Nombre Concepto")
    dest_time = fields.Float(readonly=True, string="H.Destinadas")
    add_val = fields.Float(readonly=True, string="Valor Añadido")
    waste_time = fields.Float(readonly=True, string="Horas Perdidas")
    waste_time_and_addval = fields.Float(readonly=True, string="Visual de Perdidas")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_waste_sql_table')
        self._cr.execute("""CREATE VIEW jpl_prod_waste_sql_table AS(

            select
            (5000000000+ prt.id) as id,
            rt.date as date,
            prt.id_area as id_area,
            prt.id_division as id_division,
            prt.id_center as id_center,
            prt.id_plant as id_plant,
            pt.id_cat as id_cat,
            pt.id_sub_cat as id_sub_cat,
            concat('Perdidas') as concepto,
            concat('Perdidas Calidad') as type,
            concat('SCRAP','-',pt.name) as name,
            0 as dest_time,
            0 as add_val,
            prt.scrap_time as waste_time,
            prt.scrap_time as waste_time_and_addval
            from jpl_prod_process_reg_table prt
            inner join jpl_prod_reg_table rt on (prt.reg_id = rt.id)
            inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
            union all
            select
            (6000000000+ pwrt.id) as id,
            rt.date as date,
            rt.area as id_area,
            rt.division as id_division,
            rt.center as id_center,
            rt.plant as id_plant,
            pwrt.id_cat as id_cat,
            pwrt.id_sub_cat as id_sub_cat,
            concat('Perdidas') as concepto,
            concat('Perdidas Productivas') as type,
            pwt.name as name,
            0 as dest_time,
            0 as add_val,
            pwrt.prod_wasted_time as waste_time,
            pwrt.prod_wasted_time as waste_time_and_addval
            from jpl_prod_prod_waste_reg_table pwrt
            inner join jpl_prod_reg_table rt on (pwrt.reg_id = rt.id)
            inner join jpl_prod_productivity_waste_table pwt on (pwrt.id_prod_waste = pwt.id)
            union all
            select
            (1000000000 + rt.id) as id,
            rt.date as date,
            rt.area as id_area,
            rt.division as id_division,
            rt.center as id_center,
            rt.plant as id_plant,
            1 as id_cat,
            null as id_sub_cat,
            concat('Valor') as concepto,
            concat('Valor añadido') as type,
            concat('Valor adadido en planta') as name,
            rt.dest_time as dest_time,
            rt.add_value_time as add_val,
            0 as waste_time,
            rt.add_value_time as waste_time_and_addval
            from jpl_prod_reg_table rt
            union all
            select
            (2000000000+ rt.id) as id,
            rt.date as date,
            rt.area as id_area,
            rt.division as id_division,
            rt.center as id_center,
            rt.plant as id_plant,
            1 as id_cat,
            null as id_sub_cat,
            concat('Perdidas') as concepto,
            concat('Perdidas no documentadas') as type,
            concat('Horas No asignadas') as name,
            0 as dest_time,
            0 as add_val,
            rt.hours_difference as waste_time,
            rt.hours_difference as waste_time_and_addval
            from jpl_prod_reg_table rt
            union all 
            select
            (3000000000 + irt.id) as id,
            rt.date as date,
            irt.id_area as id_area,
            irt.id_division as id_division,
            irt.id_center as id_center,
            irt.id_plant as id_plant,
            it.id_cat as id_cat,
            it.id_sub_cat as id_sub_cat,
            concat('Perdidas') as concepto,
            concat('Tiempos No Productivos') as type,
            it.name as name,
            0 as dest_time,
            0 as add_val,
            irt.dest_time as waste_time,
            irt.dest_time as waste_time_and_addval
            from jpl_prod_inef_reg_table irt
            inner join jpl_prod_reg_table rt on (irt.reg_id = rt.id)
            inner join jpl_prod_inef_table it on (irt.id_inef = it.id)
            union all 
            select
            (4000000000+ prt.id) as id,
            rt.date as date,
            prt.id_area as id_area,
            prt.id_division as id_division,
            prt.id_center as id_center,
            prt.id_plant as id_plant,
            pt.id_cat as id_cat,
            pt.id_sub_cat as id_sub_cat,
            concat('Perdidas') as concepto,
            concat('Perdidas Productivas') as type,
            concat('Ritmo lento','-',pt.name) as name,
            0 as dest_time,
            0 as add_val,
            prt.slow_rhythm_time as waste_time,
            prt.slow_rhythm_time as waste_time_and_addval
            from jpl_prod_process_reg_table prt
            inner join jpl_prod_reg_table rt on (prt.reg_id = rt.id)
            inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
                        order by id desc
            
            )""")


class UnitsEmployee(models.Model):
    _name = 'jpl_prod.units_employee'

    start_date = fields.Date(string='Dia de imputación', store=True, required=True)
    id_sap_employee = fields.Integer(string='ID Sap Empleado', store=True)
    plant = fields.Many2one('jpl_prod.plant_table', string='Planta', store=True, required=True)
    process_name = fields.Char(string='Nombre Proceso', store=True, required=True)
    type_task = fields.Selection([('Tarea', 'Tarea'),
                              ('Perdida', 'Perdida')], string='Tipo', store=True, required=True, default='Tarea')
    task_name = fields.Char(string='Nombre tarea', store=True, required=True)
    units = fields.Float(string='nº unidades', store=True, required=True)
    scrap_units = fields.Float(string='nº scrap', store=True, default=0)

    @api.depends('id_sap_employee', 'start_date', 'plant', 'process_name', 'type_task', 'task_name', 'units')
    def _computed_related_fields(self):
        for rec in self:

            rec.assigned_employee = self.env['hr.employee'].search(
                [('barcode', '=', rec.id_sap_employee)], limit=1)

            if rec.type_task == 'Tarea':
                id_process = self.env['jpl_prod.process_table'].search(
                    [('related_plant', '=', rec.plant.id), ('name', '=', rec.process_name)], limit=1)
                id_task = self.env['jpl_prod.task_table'].search(
                    [('id_related_plant', '=', rec.plant.id), ('id_related_process', '=', id_process.id),
                     ('name', '=', rec.task_name)], limit=1)

                rec.id_process = id_process
                rec.id_task = id_task
                rec.item_standard_time = id_task.standard_time
                rec.total_standard_time = (id_task.standard_time * rec.units)/3600
                rec.total_scrap_time = (id_task.standard_time * rec.scrap_units) / 3600
                rec.total_waste_time = 0.0
            else:

                id_process = self.env['jpl_prod.process_table'].search(
                    [('related_plant', '=', rec.plant.id), ('name', '=', rec.process_name)], limit=1)
                id_waste = self.env['jpl_prod.productivity_waste_table'].search(
                    [('id_related_plant', '=', rec.plant.id), ('id_process', '=', id_process.id),
                     ('name', '=', rec.task_name)], limit=1)

                rec.id_process = id_process
                rec.id_waste = id_waste
                rec.item_standard_time = id_waste.waste_standard_time
                rec.total_standard_time = 0.0
                rec.total_scrap_time = 0.0
                rec.total_waste_time = (id_waste.waste_standard_time * rec.units) / 3600

    id_process = fields.Many2one('jpl_prod.process_table', compute=_computed_related_fields, string='Proceso Asignado',
                                 store=True)
    id_task = fields.Many2one('jpl_prod.task_table', compute=_computed_related_fields, string='Tarea Asignada',
                              store=True)
    id_waste = fields.Many2one('jpl_prod.productivity_waste_table', compute=_computed_related_fields, string='Perdida Asignada',
                              store=True)
    item_standard_time = fields.Float(compute=_computed_related_fields, store=True)
    total_standard_time = fields.Float(compute=_computed_related_fields, store=True)
    total_scrap_time = fields.Float(compute=_computed_related_fields, store=True)
    total_waste_time = fields.Float(compute=_computed_related_fields, store=True)
    assigned_employee = fields.Many2one('hr.employee', compute=_computed_related_fields, string='Empleado Asignado', store=True)


class EmployeeEfficiencySlqTable(models.Model):
    _name = 'jpl_prod.employee_efficiency_sql_table'
    _auto = False

    id = fields.Integer(readonly=True)
    date = fields.Date(readonly=True, string="Fecha")
    id_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
    id_employee = fields.Many2one(comodel_name='hr.employee', string="Empleado", readonly=True)

    id_process = fields.Many2one(comodel_name='jpl_prod.process_table', string="Proceso",
                                 readonly=True)
    dest_time = fields.Float(readonly=True, string="H.Destinadas")
    id_task = fields.Many2one(comodel_name='jpl_prod.task_table', string="Tarea",
                                 readonly=True)
    units = fields.Float(readonly=True, string="Unidades")
    std_time = fields.Float(readonly=True, string="T.Standard")
    uds_h = fields.Float(readonly=True, string="Uds/h")
    perf = fields.Float(readonly=True, string="% Rend")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_employee_efficiency_sql_table')
        self._cr.execute("""CREATE VIEW jpl_prod_employee_efficiency_sql_table AS(
        
            select
            (1000000000 +att.id) as id,
            att.start_date as date,
            att.related_plant as id_plant,
            att.employee_id as id_employee,
            att.id_activity as id_process,
            att.worked_hours as dest_time,
            null as id_task,
            0 as units,
            0.00 as std_time,
            0.00 as uds_h,
            0.00 as perf
            from public.hr_attendance att
            where att.type = 'process'
            union all
            select
            (2000000000 +ue.id) as id,
            ue.start_date as date,
            ue.plant as id_plant,
            hr.id as id_employee,
            ue.id_process as id_process,
            0 as dest_time,
            ue.id_task as id_task,
            ue.units as units,
            ue.total_standard_time as std_time,
            0.00 as uds_h,
            0.00 as perf
            from jpl_prod_units_employee ue
            inner join public.hr_employee hr on (ue.assigned_employee = hr.id)
            order by id desc
            )""")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(EmployeeEfficiencySlqTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                         orderby=orderby, lazy=lazy)
        for line in res:
            if 'dest_time' in fields and 'std_time' in fields:
                if line['dest_time'] in (0, None):
                    line['perf'] = 0
                else:
                    line['perf'] = (line['std_time'] / line['dest_time']) * 100
            else:
                if 'perf' in fields:
                    fields.remove('perf')

            if 'dest_time' in fields and 'units' in fields:
                if line['dest_time'] in (0, None):
                    line['uds_h'] = 0
                else:
                    line['uds_h'] = line['units'] / line['dest_time']
            else:
                if 'uds_h' in fields:
                    fields.remove('uds_h')

        return res
