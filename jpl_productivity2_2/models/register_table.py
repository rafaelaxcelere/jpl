# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.sql import drop_view_if_exists


class RegisterTable(models.Model):
    _name = 'jpl_prod.reg_table'

    date = fields.Date(string='Fecha', default=lambda self: fields.date.today(), store=True, required=True)

    def _default_employee(self):
        return self.env['res.users'].search([('id', '=', self.env.uid)])

    employee_id = fields.Many2one('res.users', string="Employee", required=True, default=_default_employee, index=True,
                                  ondelete='set null')

    def _default_plant(self):
        return self.env['jpl_prod.plant_table'].search([('responsable', '=', self.env.uid)], limit=1)

    plant = fields.Many2one('jpl_prod.plant_table', string="Planta", default=_default_plant, index=True,
                            ondelete='set null')


    def _default_center(self):
        return self.env['jpl_prod.plant_table'].search([('responsable', '=', self.env.uid)], limit=1).related_center

    center = fields.Many2one('jpl_prod.center_table', string="Center", default=_default_center, index=True,
                             ondelete='set null')

    def _default_division(self):
        return self.env['jpl_prod.plant_table'].search([('responsable', '=', self.env.uid)],
                                                       limit=1).related_center.related_division

    division = fields.Many2one('jpl_prod.division_table', string="Division", default=_default_division, index=True,
                               ondelete='set null')

    def _default_area(self):
        return self.env['jpl_prod.plant_table'].search([('responsable', '=', self.env.uid)],
                                                       limit=1).related_center.related_division.related_area

    area = fields.Many2one('jpl_prod.area_table', string="Area", default=_default_area, index=True, ondelete='set null')

    company = fields.Text(default='GrupounoCTC')

    shift = fields.Selection([('first', 'Morning'),
                              ('second', 'Afternoon'),
                              ('third', 'Night'),
                              ], string='Shift', required=True, index=True, default='first', )
    task_reg_ids = fields.One2many('jpl_prod.task_register_table', 'reg_id', string="Task", )
    prod_reg_ids = fields.One2many('jpl_prod.prod_waste_reg_table', 'reg_id', string="ProductivityWaste", )
    process_reg_ids = fields.One2many('jpl_prod.process_reg_table', 'reg_id', string="Processes", )
    hourprocess_reg_ids = fields.One2many('jpl_prod.hourprocess_reg_table', 'reg_id', string="Hour Process", )
    inef_reg_ids = fields.One2many('jpl_prod.inef_reg_table', 'reg_id', string="Inefficiencies", )

    # To new DB use this sql_constrains
    # _sql_constraints = [
    #     ('uniq_date', 'unique(date)', 'This date is already registered'),
    # ]

    @api.constrains('date')
    def check_unique_date(self):
        for rec in self:
            if self.search([('date', '=', rec.date), ('plant', '=', rec.plant.id), ('id', '!=', rec.id)]):
                raise ValidationError(_('El registro para esta fecha ya ha sido realizado anteriromente. No pueden existir dos registros para el mismo dia.'))

            if rec.total_hours_presence == 0.0 and rec.total_hours_declared != 0:
                raise ValidationError(_('No se han declarado horas totales de presencia'))

    #@api.constrains('date')
    #def check_not_today_date(self):
    #    for rec in self:
    #        if rec.date == fields.Date.today():
    #            raise ValidationError(_(
    #                'Se está realizando un registro del dia en curso. El registro del dia en curso se ha de realizar mañana. Puede ser que hayan registros de horas no contabilizados o no finalizados.'))

    @api.onchange('date')
    def onchange_date(self):
        for rec in self:
            rec.task_reg_ids._units_registered()
            rec.prod_reg_ids._units_waste_registered()
            rec.hourprocess_reg_ids._hour_process_attendance_op_time()
            rec.process_reg_ids._process_attendance_op_time()
            rec.inef_reg_ids._inef_attendance_dest_time()

    @api.onchange('total_hours_presence')
    def onchange_hour_diference(self):
        self._computed_total_hours()

    # process
    @api.depends('process_reg_ids.billing_process', 'process_reg_ids.cost_process', 'process_reg_ids.op_time',)
    def _compute_process(self):
        for record in self:
            total_billing_process = total_cost_process = total_hours_process = 0
            for process_reg_id in record.process_reg_ids:
                total_billing_process += process_reg_id.billing_process
                total_cost_process += process_reg_id.cost_process
                total_hours_process += process_reg_id.op_time
            record.process_billing = total_billing_process
            record.process_cost = total_cost_process
            record.total_hours_process = total_hours_process
            record.margin_process = record.process_billing - record.process_cost

    process_billing = fields.Float(compute=_compute_process, store=True, string='Fact.Procesos (Eur)')
    process_cost = fields.Float(compute=_compute_process, store=True, string='Coste Procesos (Eur)')
    margin_process = fields.Float(compute=_compute_process, store=True, string='Margen Procesos (Eur)')  # hours
    total_hours_process = fields.Float(compute='_compute_process')

    @api.depends('hourprocess_reg_ids.billing_hours', 'hourprocess_reg_ids.cost_hours', 'hourprocess_reg_ids.op_time')
    def _compute_hours(self):
        for record in self:
            total_hours_billing = total_hours_cost = total_hours_hoursxprocess = 0
            for hourprocess_reg_id in record.hourprocess_reg_ids:
                total_hours_billing += hourprocess_reg_id.billing_hours
                total_hours_cost += hourprocess_reg_id.cost_hours
                total_hours_hoursxprocess += hourprocess_reg_id.op_time

            record.total_hours_hoursxprocess = total_hours_hoursxprocess
            record.hours_billing = total_hours_billing
            record.hours_cost = total_hours_cost
            record.margin_hours = record.hours_billing - record.hours_cost

    hours_billing = fields.Float(compute=_compute_hours, store=True, string='Fact.Horas (Eur)')
    hours_cost = fields.Float(compute=_compute_hours, store=True, string='Coste Horas (Eur)')
    margin_hours = fields.Float(compute=_compute_hours, store=True, string='Margen Horas (Eur)')
    total_hours_hoursxprocess = fields.Float(compute=_compute_hours)

    # Inefficiences
    @api.depends('inef_reg_ids.billing_hours', 'inef_reg_ids.cost_hours', 'inef_reg_ids.dest_time')
    def _compute_inef_hours(self):
        for record in self:
            total_inef_billing = total_inef_cost = total_hours_inef = 0
            for inef_reg_id in record.inef_reg_ids:
                total_inef_billing += inef_reg_id.billing_hours
                total_inef_cost += inef_reg_id.cost_hours
                total_hours_inef += inef_reg_id.dest_time

            record.inef_billing = total_inef_billing
            record.inef_cost = total_inef_cost
            record.margin_inef = record.inef_billing - record.inef_cost
            record.total_hours_inefficiencies = total_hours_inef

    inef_billing = fields.Float(compute=_compute_inef_hours, store=True, string='Fact.Tiempo no Product. (Eur)')
    total_hours_inefficiencies = fields.Float(compute='_compute_inef_hours')
    inef_cost = fields.Float(compute=_compute_inef_hours, store=True, string='Coste Tiempo no Product. (Eur)')
    margin_inef = fields.Float(compute=_compute_inef_hours, store=True, string='Margen Tiempo no Product. (Eur)')

    @api.depends('total_hours_inefficiencies', 'total_hours_process', 'total_hours_hoursxprocess', 'total_hours_presence')
    def _computed_total_hours(self):
        for record in self:
            record.total_hours_declared = record.total_hours_process + record.total_hours_hoursxprocess + record.total_hours_inefficiencies
            record.hours_difference = record.total_hours_presence - record.total_hours_process - record.total_hours_hoursxprocess \
                                      - record.total_hours_inefficiencies
            record.not_prod_time = record.total_hours_inefficiencies
            record.operative_time = record.total_hours_process + record.total_hours_hoursxprocess

    total_hours_declared = fields.Float(compute='_computed_total_hours', requiered=True, default=0.0, store=True)
    total_hours_presence = fields.Float(string='Horas Totales Presencia', default=0, required=True, store=True)
    hours_difference = fields.Float(compute='_computed_total_hours', default=0.0, store=True)

    @api.depends('hours_difference')
    def _compute_cost_hours_difference(self):
        for record in self:
            record.cost_hours_difference = record.hours_difference * record.plant.cost

    cost_hours_difference = fields.Float(compute='_compute_cost_hours_difference', store=True)

    # Calculo de tiempos TD, NPT, OP WPT, ST , WST, AVT
    dest_time = fields.Float(related='total_hours_presence', store=True, )
    not_prod_time = fields.Float(compute='_computed_total_hours', store=True)
    operative_time = fields.Float(compute='_computed_total_hours', store=True)

    @api.depends('operative_time', 'total_hours_hoursxprocess')
    def _compute_wasted_process_time(self):
        for record in self:
            record.wasted_process_time = record.operative_time - record.standard_time

    wasted_process_time = fields.Float(compute='_compute_wasted_process_time', store=True)

    @api.depends('total_standard_process', 'total_hours_hoursxprocess')
    def _compute_standard_time(self):
        for record in self:
            record.standard_time = record.total_standard_process + record.total_hours_hoursxprocess

    standard_time = fields.Float(compute='_compute_standard_time', store=True)

    @api.depends('task_reg_ids.scrap_wasted_time','task_reg_ids.ef_op_time')
    def _compute_total_task_reg_ids(self):
        for record in self:
            total_wasted_scrap_time = total_standard_process = 0
            for task_reg_id in record.task_reg_ids:
                total_wasted_scrap_time += task_reg_id.scrap_wasted_time
                total_standard_process += task_reg_id.ef_op_time
            record.total_standard_process = total_standard_process
            record.wasted_scrap_time = total_wasted_scrap_time

    total_standard_process = fields.Float(compute='_compute_total_task_reg_ids', store=True)
    wasted_scrap_time = fields.Float(compute='_compute_total_task_reg_ids', store=True)

    # efficiency
    disp = fields.Float(string="% Disp")
    perf = fields.Float(string="% Perf")
    qlty = fields.Float(string="% Qlty")
    oee = fields.Float(string="% OEE")
    fulfillment_oee = fields.Float(string="% Cumplimiento OEE")

    # Gross Margin
    gm100_process = fields.Float(string="MB Procesos (%)")
    gm100_hours = fields.Float(string="MB Horas (%)")
    gm100_inef = fields.Float(string="MB Tiempo No Productivo (%)")
    gm100_total = fields.Float(string="MB Total (%)")
    fulfillment_GM = fields.Float(string="% Cumplimiento MB")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(RegisterTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                    orderby=orderby, lazy=lazy)
        for line in res:
            if 'dest_time' in fields and 'operative_time' in fields:
                if line.get('dest_time', 0) in (0, None):
                    line['disp'] = 0
                else:
                    line['disp'] = line.get('operative_time', 0) / line.get('dest_time') * 100
            else:
                if 'disp' in fields:
                    fields.remove('disp')

            if 'operative_time' in fields and 'standard_time' in fields:
                if line.get('operative_time', 0) in (0, None):
                    line['perf'] = 0
                else:
                    line['perf'] = line.get('standard_time', 0) / line.get('operative_time') * 100
            else:
                if 'perf' in fields:
                    fields.remove('perf')

            if 'add_value_time' in fields and 'standard_time' in fields:
                if line.get('standard_time', 0) in (0, None):
                    line['qlty'] = 0
                else:
                    line['qlty'] = line.get('add_value_time', 0) / line.get('standard_time') * 100
            else:
                if 'qlty' in fields:
                    fields.remove('qlty')

            if 'add_value_time' in fields and 'dest_time' in fields:
                if line.get('dest_time', 0) in (0, None):
                    line['oee'] = 0
                else:
                    line['oee'] = line.get('add_value_time', 0) / line.get('dest_time') * 100
            else:
                if 'oee' in fields:
                    fields.remove('oee')

            if 'oee' in fields and 'oee_objective' in fields:
                if line.get('oee', 0) in (0, None):
                    line['fulfillment_oee'] = 0
                else:
                    line['fulfillment_oee'] = line.get('oee') - line['oee_objective']
            else:
                if 'fulfillment_oee' in fields:
                    fields.remove('fulfillment_oee')
            # gross margin
            if 'process_billing' in fields and 'margin_process' in fields:
                if line.get('process_billing', 0) in (0, None):
                    line['gm100_process'] = 0
                else:
                    line['gm100_process'] = line.get('margin_process', 0) / line.get('process_billing') * 100
            else:
                if 'gm100_process' in fields:
                    fields.remove('gm100_process')

            if 'hours_billing' in fields and 'margin_hours' in fields:
                if line.get('hours_billing', 0) in (0, None):
                    line['gm100_hours'] = 0
                else:
                    line['gm100_hours'] = line.get('margin_hours', 0) / line.get('hours_billing') * 100
            else:
                if 'gm100_hours' in fields:
                    fields.remove('gm100_hours')

            if 'inef_billing' in fields and 'margin_inef' in fields:
                if line.get('inef_billing', 0) in (0, None):
                    line['gm100_inef'] = 0
                else:
                    line['gm100_inef'] = line['margin_inef'] / line['inef_billing'] * 100
            else:
                if 'gm100_inef' in fields:
                    fields.remove('gm100_inef')

            if 'total_billing' in fields and 'margin_total' in fields:
                if line.get('total_billing', 0) in (0, None):
                    line['gm100_total'] = 0
                else:
                    line['gm100_total'] = line['margin_total'] / line['total_billing'] * 100
            else:
                if 'gm100_total' in fields:
                    fields.remove('gm100_total')

            if 'gm100_total' in fields and 'gm_objective' in fields:
                if line.get('gm100_total', 0) in (0, None):
                    line['fulfillment_GM '] = 0
                else:
                    line['fulfillment_GM'] = line.get('gm100_total') - line['gm_objective']
            else:
                if 'fulfillment_GM' in fields:
                    fields.remove('fulfillment_GM')

        return res

    add_value_time = fields.Float(compute='_compute_add_value_time', store=True, )

    @api.depends('wasted_scrap_time', 'standard_time')
    def _compute_add_value_time(self):
        for record in self:
            record.add_value_time = record.standard_time - record.wasted_scrap_time

    # Economical parameters.

    # total
    @api.depends('process_billing', 'hours_billing', 'inef_billing')
    def _computed_billing(self):
        for record in self:
            record.total_billing = record.process_billing + record.hours_billing + record.inef_billing

    total_billing = fields.Float(compute=_computed_billing, store=True, string='Fact.Total (Eur)')

    @api.depends('process_cost', 'hours_cost', 'inef_cost', 'cost_hours_difference')
    def _computed_cost(self):
        for record in self:
            record.total_cost = record.process_cost + record.hours_cost + record.inef_cost + record.cost_hours_difference

    total_cost = fields.Float(compute=_computed_cost, store=True, string='Coste Total (Eur)')

    @api.depends('total_billing', 'total_cost')
    def _computed_mb_total(self):
        for record in self:
            record.margin_total = record.total_billing - record.total_cost

    margin_total = fields.Float(compute=_computed_mb_total, store=True, string='Margen Total (Eur)')

    # Objectives
    @api.depends('plant')
    def _computed_obj(self):
        for record in self:
            record.gm_objective = record.plant.gm_objective
            record.oee_objective = record.plant.oee_objective
            record.oee_limit = record.plant.oee_limit

    gm_objective = fields.Float(compute=_computed_obj, default=7, group_operator='avg', string='Objetivo Margen Bruto (%)', store=True,
                                readonly=True, required=True)
    oee_objective = fields.Float(compute=_computed_obj, default=65, group_operator='avg',
                                 string='Objetivo OEE (%)', store=True,
                                 readonly=True, required=True)
    oee_limit = fields.Float(compute=_computed_obj, default=50, group_operator='avg',
                             string='Objetivo OEE (%)', store=True,
                             readonly=True, required=True)

    @api.model
    def default_get(self, fields_list):
        # call to default function
        res = super(RegisterTable, self).default_get(fields_list)

        userPlant = self.env['jpl_prod.plant_table'].search([('responsable', '=', self.env.uid)], limit=1)

        # add processes que tenga encuenta los activos solamente
        possible_processes = self.env['jpl_prod.process_table'].search([('related_plant', '=', userPlant.id), ('active', '!=', False)])
        created_processes_records = []
        for process in possible_processes:
            created_processes_records.append((0, 0, {'id_process': process.id}))
        res['process_reg_ids'] = created_processes_records

        # add inefficiencies
        possible_inefficiencies = self.env['jpl_prod.inef_table'].search([('related_plant', '=', userPlant.id), ('active', '!=', False)])
        created_inefficiencies_records = []
        for inefficiency in possible_inefficiencies:
            created_inefficiencies_records.append((0, 0, {'id_inef': inefficiency.id}))
        res['inef_reg_ids'] = created_inefficiencies_records

        # add hours processes
        possible_hoursprocesses = self.env['jpl_prod.hourprocess_table'].search([('related_plant', '=', userPlant.id), ('active', '!=', False)])
        created_hoursprocesses_records = []
        for hourprocess in possible_hoursprocesses:
            created_hoursprocesses_records.append((0, 0, {'id_processxhours': hourprocess.id}))
        res['hourprocess_reg_ids'] = created_hoursprocesses_records

        # add tasks
        possible_tasks = self.env['jpl_prod.task_table'].search([('id_related_plant', '=', userPlant.id), ('active', '!=', False)])
        created_tasks_records = []
        for task in possible_tasks:
            related_process_name = task.id_related_process.name
            elementary_unit = task.elementary_unit
            created_tasks_records.append(
                (0, 0, {'order': task.form_order,'id_task': task.id, 'related_process_on_task_view': related_process_name,
                        'elementary_unit_on_task_view': elementary_unit}))
        res['task_reg_ids'] = created_tasks_records

        # add processes productivity waste
        possible_processes_productivity_waste = self.env['jpl_prod.productivity_waste_table'].search(
            [('id_related_plant', '=', userPlant.id), ('active', '!=', False)])
        created_processes_productivity_waste_records = []
        for process_productivity_waste in possible_processes_productivity_waste:
            related_process_name = process_productivity_waste.id_process.name
            created_processes_productivity_waste_records.append(
                (0, 0,
                 {'id_prod_waste': process_productivity_waste.id, 'related_process_on_task': related_process_name}))
        res['prod_reg_ids'] = created_processes_productivity_waste_records

        return res

class OeeSlqTable(models.Model):
    _name = 'jpl_prod.oee_sql_table'
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
    name = fields.Char(readonly=True, string="Nombre")
    dest_time = fields.Float(readonly=True, string="T.Presencia(H)")
    hours_difference = fields.Float(readonly=True, string="T.NoDocum(H)")
    hours_declared = fields.Float(readonly=True, string="T.Declarado(H)")
    not_op_time = fields.Float(readonly=True, string="T.NoOperativo(H)")
    op_time = fields.Float(readonly=True, string="T.Operativo(H)")
    waste_time = fields.Float(readonly=True, string="T.Per.Produc.(H)")
    std_time = fields.Float(readonly=True, string="T.STD(H)")
    scarp_time = fields.Float(readonly=True, string="Perdida Calidad(H)")
    added_val_time = fields.Float(readonly=True, string="Val.Añadido(H)")
    disp = fields.Float(string="% Disp")
    perf = fields.Float(string="% Perf")
    qlty = fields.Float(string="% Qlty")
    oee = fields.Float(string="% OEE")
    oee_objective = fields.Float(string='Obj.OEE(%)', group_operator='avg', readonly=True)
    fulfillment_oee = fields.Float(string="Cumpl.OEE(%)")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_oee_sql_table')
        self._cr.execute("""CREATE VIEW jpl_prod_oee_sql_table AS(
        
        select 
        (1000000000 + rt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        1 as id_cat,
        null as id_sub_cat,
        concat('Global') as concepto,
        concat('Global') as name,
        rt.dest_time as dest_time,
        rt.hours_difference as hours_difference,
        0 as hours_declared,
        0 as not_op_time,
        0 as op_time,
        0 as waste_time,
        0 as std_time,
        0 as scarp_time,
        0 as added_val_time,
        rt.disp as disp,
        rt.perf as perf,
        rt.qlty as qlty,
        rt.oee as oee,
        rt.oee_objective as oee_objective,
        rt.fulfillment_oee as fulfillment_oee
        from jpl_prod_reg_table rt
        union all
        select 
        (2000000000 + prt.id) as id,
        rt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        prt.id_category as id_cat,
        prt.id_subcategory as id_sub_cat,
        concat('Procesos') as concepto,
        pt.name as name,
        0 as dest_time,
        0 as hours_difference,
        prt.op_time as hours_declared,
        0 as not_op_time,
        prt.op_time as op_time,
        (prt.op_time-prt.standard_time_in_process) as waste_time,
        prt.standard_time_in_process as std_time,
        (prt.standard_time_in_process - prt.add_val_time_in_process) as scarp_time,
        prt.add_val_time_in_process as added_val_time,
        rt.disp as disp,
        rt.perf as perf,
        rt.qlty as qlty,
        rt.oee as oee,
        rt.oee_objective as oee_objective,
        rt.fulfillment_oee as fulfillment_oee
        from jpl_prod_process_reg_table prt
        inner join jpl_prod_process_table pt on (prt.id_process=pt.id)
        inner join jpl_prod_reg_table rt on (prt.reg_id = rt.id)
        union all
        select 
        (3000000000 + irt.id) as id,
        rt.date as date,
        irt.id_area as id_area,
        irt.id_division as id_division,
        irt.id_center as id_center,
        irt.id_plant as id_plant,
        irt.id_category as id_cat,
        irt.id_subcategory as id_sub_cat,
        concat('Tiempos No productivos') as concepto,
        it.name as name,
        0 as dest_time,
        0 as hours_difference,
        irt.dest_time as hours_declared,
        irt.dest_time as not_op_time,
        0 as op_time,
        0 as waste_time,
        0 as std_time,
        0 as scarp_time,
        0 as added_val_time,
        rt.disp as disp,
        rt.perf as perf,
        rt.qlty as qlty,
        rt.oee as oee,
        rt.oee_objective as oee_objectivej,
        rt.fulfillment_oee as fulfillment_oee
        from jpl_prod_inef_reg_table irt
        inner join jpl_prod_inef_table it on (irt.id_inef = it.id)
        inner join jpl_prod_reg_table rt on (irt.reg_id = rt.id)
        union all
        select
        (4000000000 + hrt.id) as id,
        rt.date as date,
        hrt.id_area as id_area,
        hrt.id_division as id_division,
        hrt.id_center as id_center,
        hrt.id_plant as id_plant,
        hrt.id_category as id_cat,
        hrt.id_subcategory as id_sub_cat,
        concat('Procesos a Horas') as concepto,
        ht.name as name,
        0 as dest_time,
        0 as hours_difference,
        hrt.op_time as hours_declared,
        0 as not_op_time,
        hrt.op_time as op_time,
        0 as waste_time,
        hrt.op_time as std_time,
        0 as scarp_time,
        hrt.op_time as added_val_time,
        rt.disp as disp,
        rt.perf as perf,
        rt.qlty as qlty,
        rt.oee as oee,
        rt.oee_objective as oee_objective,
        rt.fulfillment_oee as fulfillment_oee
        from jpl_prod_hourprocess_reg_table hrt
        inner join jpl_prod_hourprocess_table ht on (hrt.id_processxhours = ht.id)
        inner join jpl_prod_reg_table rt on (hrt.reg_id = rt.id)
                         
        )""")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(OeeSlqTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                    orderby=orderby, lazy=lazy)
        for line in res:
            if 'op_time' in fields and 'dest_time' in fields and 'hours_declared' in fields:
                if line['dest_time'] in (0, None):
                    if line['hours_declared'] in (0, None):
                        line['disp'] = 0
                    else:
                        line['disp'] = (line['op_time'] / line['hours_declared']) * 100
                else:
                    line['disp'] = (line['op_time'] / line['dest_time']) * 100
            else:
                if 'disp' in fields:
                    fields.remove('disp')

            if 'std_time' in fields and 'op_time' in fields:
                if line['op_time'] in (0, None):
                    line['perf'] = 0
                else:
                    line['perf'] = line['std_time'] / line['op_time'] * 100
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

            if 'disp' in fields and 'perf' in fields and 'qlty' in fields:
                line['oee'] = line['disp'] * line['perf'] * line['qlty'] / 10000
            else:
                if 'oee' in fields:
                    fields.remove('oee')

            if 'oee' in fields and 'oee_objective' in fields:
                if line.get('oee', 0) in (0, None):
                    line['fulfillment_oee'] = 0
                else:
                    line['fulfillment_oee'] = line['oee'] - line['oee_objective']
            else:
                if 'fulfillment_oee' in fields:
                    fields.remove('fulfillment_oee')

        return res

class CcmSqlTable(models.Model):
    _name = 'jpl_prod.ccm_sql_table'
    _auto = False

    id = fields.Integer(readonly=True)
    date = fields.Date(readonly=True, string="Fecha")
    id_area = fields.Many2one(comodel_name='jpl_prod.area_table', string="Area", readonly=True)
    id_division = fields.Many2one(comodel_name='jpl_prod.division_table', string="Division", readonly=True)
    id_center = fields.Many2one(comodel_name='jpl_prod.center_table', string="Centro", readonly=True)
    id_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
    id_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Categoria", readonly=True)
    type_process = fields.Char(readonly=True, string="Concepto")
    id_sub_cat = fields.Many2one(comodel_name='jpl_prod.process_sub_category_table', string="Subcategoria", readonly=True)
    process_name = fields.Char(readonly=True, string="Proceso")
    dest_hours = fields.Float(readonly=True, string="H.Destinadas")
    task_name = fields.Char(readonly=True, string="Tareas")
    units = fields.Float(string="Unidades")
    std_hours = fields.Float(readonly=True, string="H.Objetivo")
    wast_hours = fields.Float(readonly=True, string="H.Perdidas")
    efficiency = fields.Float(string="% Eficiencia")
    productivity = fields.Float(string="Uds/h")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_ccm_sql_table')
        self._cr.execute("""CREATE VIEW jpl_prod_ccm_sql_table AS(
        
        SELECT
        (1000000000 + rt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        1 as id_cat,
        'T.no productivos' as type_process,
        null as id_sub_cat,
        'h. no documentadas' as process_name,
        rt.hours_difference as dest_hours,
        '' as task_name,
        0 as units,
        0 as std_hours,
        rt.hours_difference as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_reg_table rt
        union all 
        select
        (2000000000 + irt.id) as id,
        rt.date as date,
        irt.id_area as id_area,
        irt.id_division as id_division,
        irt.id_center as id_center,
        irt.id_plant as id_plant,
        irt.id_category id_cat,
        'T.no productivos' as type_process,
        irt.id_subcategory as id_sub_cat,
        it.name as process_name,
        irt.dest_time as dest_hours,
        '' as task_name,
        0 as units,
        0 as std_hours,
        irt.dest_time as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_inef_reg_table irt
        inner join jpl_prod_inef_table it on (irt.id_inef = it.id)
        inner join jpl_prod_reg_table rt on (irt.reg_id = rt.id)
        union all
        select
        (3000000000 + hrt.id) as id,
        rt.date as date,
        hrt.id_area as id_area,
        hrt.id_division as id_division,
        hrt.id_center as id_center,
        hrt.id_plant as id_plant,
        hrt.id_category id_cat,
        'Procesos a horas' as type_process,
        hrt.id_subcategory as id_sub_cat,
        ht.name as process_name,
        hrt.op_time as dest_hours,
        '' as task_name,
        0 as units,
        hrt.op_time as std_hours,
        0 as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_hourprocess_reg_table hrt
        inner join jpl_prod_hourprocess_table ht on (hrt.id_processxhours = ht.id)
        inner join jpl_prod_reg_table rt on (hrt.reg_id = rt.id)
        union all
        select
        (4000000000 + prt.id) as id,
        rt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        prt.id_category id_cat,
        'Procesos' as type_process,
        prt.id_subcategory as id_sub_cat,
        pt.name as process_name,
        prt.op_time as dest_hours,
        '' as task_name,
        0 as units,
        0 as std_hours,
        0 as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_process_reg_table prt
        inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
        inner join jpl_prod_reg_table rt on (prt.reg_id = rt.id)
        union all
        select
        (5000000000 + trt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        pt.id_cat id_cat,
        'Procesos' as type_process,
        pt.id_sub_cat as id_sub_cat,
        pt.name as process_name,
        0 as dest_hours,
        tt.name as task_name,
        trt.units as units,
        (case when pt.effxprocess_objective=0 then 0 else trt.ef_op_time/(pt.effxprocess_objective/100) end) as std_hours,
        0 as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_task_register_table trt
        inner join jpl_prod_task_table tt on ( trt.id_task = tt.id)
        inner join jpl_prod_process_table pt on (trt.related_process = pt.id)
        inner join jpl_prod_reg_table rt on (trt.reg_id = rt.id)
        union all
        select
        (6000000000 + pwrt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        pt.id_cat id_cat,
        'Procesos' as type_process,
        pt.id_sub_cat as id_sub_cat,
        pt.name as process_name,
        0 as dest_hours,
        pwt.name as task_name,
        0 as units,
        0 as std_hours,
        pwrt.prod_wasted_time as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_prod_waste_reg_table pwrt
        inner join jpl_prod_productivity_waste_table pwt on ( pwrt.id_prod_waste = pwt.id)
        inner join jpl_prod_process_table pt on (pwrt.related_process = pt.id)
        inner join jpl_prod_reg_table rt on (pwrt.reg_id = rt.id)
        union all
        select
        (7000000000 + prt.id) as id,
        rt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        prt.id_category id_cat,
        'Procesos' as type_process,
        prt.id_subcategory as id_sub_cat,
        pt.name as process_name,
        0 as dest_hours,
        'Ritmo lento' as task_name,
        0 as units,
        0 as std_hours,
        prt.slow_rhythm_time as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_process_reg_table prt
        inner join jpl_prod_process_table pt on (prt.id_process = pt.id)
        inner join jpl_prod_reg_table rt on (prt.reg_id = rt.id)
        union all
        select
        (8000000000 + trt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        pt.id_cat id_cat,
        'Procesos' as type_process,
        pt.id_sub_cat as id_sub_cat,
        pt.name as process_name,
        0 as dest_hours,
        'Compensación Objetivo al Ritmo lento' as task_name,
        0 as units,
        0 as std_hours,
        (case when pt.effxprocess_objective=0 then 0 else trt.ef_op_time - trt.ef_op_time/(pt.effxprocess_objective/100)end) as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_task_register_table trt
        inner join jpl_prod_task_table tt on ( trt.id_task = tt.id)
        inner join jpl_prod_process_table pt on (trt.related_process = pt.id)
        inner join jpl_prod_reg_table rt on (trt.reg_id = rt.id)
        union all
        SELECT
        (9000000000 + rt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        1 as id_cat,
        'T.no productivos' as type_process,
        null as id_sub_cat,
        '1. Objetivo Disponibilidad' as process_name,
        0 as dest_hours,
        '' as task_name,
        0 as units,
        rt.total_hours_presence - rt.total_hours_presence*(pt.disp_objective/100) as std_hours,
        -1*(rt.total_hours_presence - rt.total_hours_presence*(pt.disp_objective/100)) as wast_hours,
        0 as efficiency,
        0 as productivity
        from jpl_prod_reg_table rt
        inner join jpl_prod_plant_table pt on (rt.plant = pt.id)

        )""")

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(CcmSqlTable, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        for line in res:
            if 'dest_hours' in fields and 'std_hours' in fields:
                if line['dest_hours'] in (0, None):
                   line['efficiency'] = 0
                else:
                    line['efficiency'] = (line['std_hours'] / line['dest_hours']) * 100
            else:
                if 'dest_hours' in fields:
                    fields.remove('efficiency')

            if 'units' in fields and 'dest_hours' in fields:
                if line['dest_hours'] in (0, None):
                    line['productivity'] = 0
                else:
                    line['productivity'] = line['units'] / line['dest_hours']
            else:
                if 'productivity' in fields:
                    fields.remove('productivity')

        return res
