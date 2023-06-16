# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.tools.sql import drop_view_if_exists

class OEEGraphics(models.Model):
    _name = 'jpl_prod.oee_graphic'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    reg_id = fields.Integer(readonly=True, store=True, ondelete='set null')
    date = fields.Date(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    concept = fields.Text(readonly=True, store=True, ondelete='set null')
    name = fields.Text(readonly=True, store=True, ondelete='set null')
    qty = fields.Float(readonly=True, store=True, ondelete='set null')
    wasted_qty = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_oee_graphic')
        self._cr.execute(""" CREATE VIEW jpl_prod_oee_graphic AS (
             SELECT 
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Destinated time' as concept,
             'Destinated time' as name,
             rt.dest_time as qty,
             0 as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Lost Hours' as concept,
             CONCAT('Lost Hours',' ',pt.name) as name,
             rt.hours_difference as qty,
             rt.hours_difference as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             npt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Not Productive time' as concept,
             it.name as name,
             npt.dest_time as qty,
             npt.dest_time as wasted_qty
             FROM jpl_prod_reg_table rt 
             INNER JOIN jpl_prod_inef_reg_table npt on (npt.reg_id=rt.id)
             INNER JOIN jpl_prod_inef_table it on (it.id=npt.id_inef)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=npt.id_plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             prt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Operative Time' as concept,
             ppt.name as name,
             prt.op_time as qty,
             0 as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_process_reg_table prt on (prt.reg_id=rt.id)
             INNER JOIN jpl_prod_process_table ppt on (ppt.id=prt.id_process)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=prt.id_plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             hrt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Operative Time' as concept,
             hpt.name as name,
             hrt.op_time as qty,
             0 as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_hourprocess_reg_table hrt on (hrt.reg_id=rt.id)
             INNER JOIN jpl_prod_hourprocess_table hpt on (hpt.id=hrt.id_processxhours)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=hrt.id_plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Productivity Waste Time' as concept,
             CONCAT(pwt.name,' ',wrt.related_process_on_task) as name,
             wrt.prod_wasted_time as qty,
             wrt.prod_wasted_time as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_prod_waste_reg_table wrt on (wrt.reg_id=rt.id)
             INNER JOIN jpl_prod_productivity_waste_table pwt on (pwt.id=wrt.id_prod_waste)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Productivity Waste Time' as concept,
             CONCAT('Slow rhythm',' ',pst.name) as name,
             prt.slow_rhythm_time as qty,
             prt.slow_rhythm_time as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_process_reg_table prt on (prt.reg_id=rt.id)
             INNER JOIN jpl_prod_process_table pst on (pst.id=prt.id_process)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Standard Time' as concept,
             pst.name as name,
             prt.standard_time_in_process as qty,
             0 as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_process_reg_table prt on (prt.reg_id=rt.id)
             INNER JOIN jpl_prod_process_table pst on (pst.id=prt.id_process)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Scrap Time' as concept,
             CONCAT('Scrap Time ',pst.name) as name,
             prt.scrap_time as qty,
             prt.scrap_time as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_process_reg_table prt on (prt.reg_id=rt.id)
             INNER JOIN jpl_prod_process_table pst on (pst.id=prt.id_process)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             UNION ALL
             SELECT
             1 as id,
             rt.id as reg_id,
             rt.date,
             pt.name as plant,
             pt.id as plant_id,
             'Added Value Time' as concept,
             pst.name as name,
             prt.add_val_time_in_process as qty,
             0 as wasted_qty
             FROM jpl_prod_reg_table rt
             INNER JOIN jpl_prod_process_reg_table prt on (prt.reg_id=rt.id)
             INNER JOIN jpl_prod_process_table pst on (pst.id=prt.id_process)
             INNER JOIN jpl_prod_plant_table pt on (pt.id=rt.plant)
             order by wasted_qty
             )""")


class Extra_invoice(models.Model):
    _name = 'jpl_prod.extra_invoice'

    date = fields.Date(default=lambda self: fields.date.today(), string='Fecha de imputación', store=True, required=True, ondelete='set null')
    concept = fields.Many2one('jpl_prod.extra_invoice_concept_list', string='Concepto', store=True, required=True, ondelete='set null')
    description = fields.Text(string='Descripción', required=True, store=True, ondelete='set null')
    extra_billing = fields.Float(string='€ Facturacion', store=True, required=True, ondelete='set null', defautl=0.0)
    extra_cost = fields.Float(string='€ Coste', store=True, required=True, ondelete='set null', defautl=0.0)
    related_plant = fields.Many2one('jpl_prod.plant_table', string='Planta', required=True, store=True, ondelete='set null')
    id_area = fields.Many2one(related='related_plant.related_center.related_division.related_area',
                              string='Area', store=True, readonly=True, ondelete='set null')
    id_division = fields.Many2one(related='related_plant.related_center.related_division',
                                  string='Division',
                                  store=True, readonly=True, ondelete='set null')
    id_center = fields.Many2one(related='related_plant.related_center', string='Center', store=True,
                                readonly=True, ondelete='set null')

    id_cat = fields.Many2one('jpl_prod.process_category_table', ondelete='set null', string="Category",
                             index=False, required=True)
    id_sub_cat = fields.Many2one('jpl_prod.process_sub_category_table', ondelete='set null', string="Subcategory",
                             index=False)

    @api.depends('date')
    def _computed_gm(self):
        for record in self:
            record.gm_obj_on_creation = record.related_plant.gm_objective

    gm_obj_on_creation = fields.Float(compute='_computed_gm', default=0.00, store=True, readonly=True)


class ExtraInvoice(models.Model):
    _name = 'jpl_prod.extra_invoice_concept_list'

    name = fields.Text(string='Nombre', required=True, store=True, ondelete='set null')
    description = fields.Text(string='Descripción', store=True, ondelete='set null')


class Invoice(models.Model):
    _name = 'jpl_prod.invoice'
    _auto = False

    date = fields.Date(readonly=True, ondelete='set null', string="Fecha")
    area_id = fields.Many2one(comodel_name='jpl_prod.area_table', string="Area")
    division_id = fields.Many2one(comodel_name='jpl_prod.division_table', string="Division")
    center_id = fields.Many2one(comodel_name='jpl_prod.center_table', string="Centro")
    plant_id = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta")
    type = fields.Char(readonly=True, string="Concepto")
    id_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Categoria")
    id_sub_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Subcategoria")
    name = fields.Char(readonly=True, ondelete='set null', string="Nombre")
    units = fields.Float(readonly=True, ondelete='set null', string="Unidades")
    price = fields.Float(readonly=True, group_operator='avg', ondelete='set null', string="Precio €/ud.")
    billing = fields.Float(readonly=True, ondelete='set null', string="Total €")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_invoice')
        self._cr.execute(""" CREATE VIEW jpl_prod_invoice AS (
        
        SELECT
        (1000000000 + trt.id) as id,
        rt.date as date,
        rt.area as area_id,
        rt.division as division_id,
        rt.center as center_id,
        rt.plant as plant_id,
        'Unidades' as type,
        trt.id_cat as id_cat,
        trt.id_sub_cat as id_sub_cat,
        tt.name as name,
        trt.units as units,
        trt.price as price,
        (trt.price * trt.units) as billing
        from jpl_prod_task_register_table trt 
        inner join jpl_prod_reg_table rt on (trt.reg_id = rt.id)
        inner join jpl_prod_task_table tt on (trt.id_task = tt.id)
        union all
        select
        (2000000000 + pwrt.id) as id,
        rt.date as date,
        rt.area as area_id,
        rt.division as division_id,
        rt.center as center_id,
        rt.plant as plant_id,
        'Perdidas productivas' as type,
        pwrt.id_cat as id_cat,
        pwrt.id_sub_cat as id_sub_cat,
        pwt.name as name,
        pwrt.units as units,
        pwrt.price as price,
        (pwrt.price * pwrt.units) as billing
        from jpl_prod_prod_waste_reg_table pwrt 
        inner join jpl_prod_reg_table rt on (pwrt.reg_id = rt.id)
        inner join jpl_prod_productivity_waste_table pwt on (pwrt.id_prod_waste = pwt.id)
        union all
        select 
        (3000000000 + irt.id) as id,
        rt.date as date,
        rt.area as area_id,
        rt.division as division_id,
        rt.center as center_id,
        rt.plant as plant_id,
        'Tiempos no productivos' as type,
        it.id_cat as id_cat,
        it.id_sub_cat as id_sub_cat,
        it.name as name,
        irt.dest_time as units,
        irt.price as price,
        (irt.price * irt.dest_time) as billing
        from jpl_prod_inef_reg_table irt 
        inner join jpl_prod_reg_table rt on (irt.reg_id = rt.id)
        inner join jpl_prod_inef_table it on (irt.id_inef = it.id)
        union all
        select 
        (4000000000 + hrt.id) as id,
        rt.date as date,
        rt.area as area_id,
        rt.division as division_id,
        rt.center as center_id,
        rt.plant as plant_id,
        'Facturacion a horas' as type,
        ht.id_cat as id_cat,
        ht.id_sub_cat as id_sub_cat,
        ht.name as name,
        hrt.op_time as units,
        hrt.price as price,
        (hrt.price * hrt.op_time) as billing
        from jpl_prod_hourprocess_reg_table hrt 
        inner join jpl_prod_reg_table rt on (hrt.reg_id = rt.id)
        inner join jpl_prod_hourprocess_table ht on (hrt.id_processxhours = ht.id)
        union all
        select 
        (5000000000 + ei.id) as id,
        ei.date as date,
        ei.id_area as area_id,
        ei.id_division as division_id,
        ei.id_center as center_id,
        ei.related_plant as plant_id,
        'Extras factura' as type,
        ei.id_cat as id_cat,
        ei.id_sub_cat as id_sub_cat,
        ei.description as name,
        1 as units,
        ei.extra_billing as price,
        ei.extra_billing as billing
        from jpl_prod_extra_invoice ei

                         )""")



class EstimatedGrossMargin(models.Model):
    _name = 'jpl_prod.est_gross_margin'
    _auto = False

    id = fields.Integer(readonly=True, ondelete='set null')
    date = fields.Date(readonly=True, ondelete='set null')
    id_area = fields.Many2one(comodel_name='jpl_prod.area_table', string="Area", readonly=True)
    id_division = fields.Many2one(comodel_name='jpl_prod.division_table', string="Division", readonly=True)
    id_center = fields.Many2one(comodel_name='jpl_prod.center_table', string="Centro", readonly=True)
    id_plant = fields.Many2one(comodel_name='jpl_prod.plant_table', string="Planta", readonly=True)
    id_cat = fields.Many2one(comodel_name='jpl_prod.process_category_table', string="Categoria", readonly=True)
    id_sub_cat = fields.Many2one(comodel_name='jpl_prod.process_sub_category_table', string="Subcategoria", readonly=True)
    type = fields.Char(readonly=True, string="Concepto")
    name = fields.Char(readonly=True, string="Nombre")
    total_cost = fields.Float(readonly=True)
    total_fact = fields.Float(readonly=True)

    gm_obj = fields.Float(readonly=True, group_operator='avg')
    gm_total = fields.Float(string="Est. Masa Margen")
    gm100_total = fields.Float(string="Est. MB(%)")
    fulfillment_gm = fields.Float(string="% Cumpl. MB")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_est_gross_margin')
        self._cr.execute("""CREATE VIEW jpl_prod_est_gross_margin AS(
        
        with cte as ( select 
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
            he.plant_id,
            hh.employee_cost
            from public.hr_holidays as hh
            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
            inner join public.hr_employee as he on (hh.employee_id = he.id)
            union all
            select
            (2000000000 + hh.id) as id, 
            hh.date_from as d_from, 
            hh.date_to as d_to, 
            date(hh.date_from + interval '1' day) as start_date,
            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day, 
            hh.holiday_status_id, 
            hh.employee_id, 
            hh.number_of_days_temp, 
            hs.name,
            hs.x100_cost,
            he.barcode,
            he.identification_id,
            he.plant_id,
            hh.employee_cost
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
            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day,
            hh.holiday_status_id, 
            hh.employee_id, 
            hh.number_of_days_temp, 
            hs.name,
            hs.x100_cost,
            he.barcode,
            he.identification_id,
            he.plant_id,
            hh.employee_cost
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
            EXTRACT(epoch from (hh.date_to - (hh.date_from + ((hh.number_of_days_temp-1)*interval'1' day))))/3600 as hours_Day,
            hh.holiday_status_id, 
            hh.employee_id, 
            hh.number_of_days_temp, 
            hs.name,
            hs.x100_cost,
            he.barcode,
            he.identification_id,
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
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
            he.plant_id,
            hh.employee_cost
            from public.hr_holidays as hh
            inner join public.hr_holidays_status as hs on (hh.holiday_status_id = hs.id)
            inner join public.hr_employee as he on (hh.employee_id = he.id)
            where 31 <= number_of_days_temp)
        select 
        (1000000000 + prt.id) as id,
        prt.date as date,
        prt.id_area as id_area,
        prt.id_division as id_division,
        prt.id_center as id_center,
        prt.id_plant as id_plant,
        prt.id_category as id_cat,
        prt.id_subcategory as id_sub_cat,
        concat('Procesos')as type,
        pt.name as name,
        prt.cost_process as total_cost,
        prt.billing_process  as total_fact,
        rt.gm_objective as gm_obj,
        (prt.billing_process - prt.cost_process) gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from jpl_prod_process_reg_table  as prt
        inner join jpl_prod_process_table pt on (prt.id_process= pt.id)
        inner join jpl_prod_reg_table rt on (prt.reg_id= rt.id)
        union all
        select
        (2000000000 + irt.id) as id,
        irt.date as date,
        irt.id_area as id_area,
        irt.id_division as id_division,
        irt.id_center as id_center,
        irt.id_plant as id_plant,
        irt.id_category as id_cat,
        irt.id_subcategory as id_sub_cat,
        concat('Tiempos no productivos')as type,
        it.name as name,
        irt.cost_hours as total_cost,
        irt.billing_hours  as total_fact,
        rt.gm_objective as gm_obj,
        (irt.billing_hours - irt.cost_hours) gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from jpl_prod_inef_reg_table  as irt
        inner join jpl_prod_inef_table it on (irt.id_inef= it.id)
        inner join jpl_prod_reg_table rt on (irt.reg_id= rt.id)
        union all
        select
        (3000000000 + hrt.id) as id,
        hrt.date as date,
        hrt.id_area as id_area,
        hrt.id_division as id_division,
        hrt.id_center as id_center,
        hrt.id_plant as id_plant,
        hrt.id_category as id_cat,
        hrt.id_subcategory as id_sub_cat,
        concat('Procesos a horas')as type,
        ht.name as name,
        hrt.cost_hours as total_cost,
        hrt.billing_hours  as total_fact,
        rt.gm_objective as gm_obj,
        (hrt.billing_hours - hrt.cost_hours) gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from jpl_prod_hourprocess_reg_table  as hrt
        inner join jpl_prod_hourprocess_table ht on (hrt.id_processxhours= ht.id)
        inner join jpl_prod_reg_table rt on (hrt.reg_id= rt.id)
        union all
        select
        (4000000000 + ei.id) as id,
        ei.date as date,
        ei.id_area as id_area,
        ei.id_division as id_division,
        ei.id_center as id_center,
        ei.related_plant as id_plant,
        ei.id_cat as id_cat,
        ei.id_sub_cat as id_sub_cat,
        concat('ExtrasFact/Cost')as type,
        concat(eic.name,' / ',ei.description) as name,
        ei.extra_cost as total_cost,
        ei.extra_billing  as total_fact,
        ei.gm_obj_on_creation as gm_obj,
        (ei.extra_billing - ei.extra_cost) gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from jpl_prod_extra_invoice  as ei
        inner join jpl_prod_extra_invoice_concept_list eic on (ei.concept=eic.id)
        union all
        select
        (5000000000 + rt.id) as id,
        rt.date as date,
        rt.area as id_area,
        rt.division as id_division,
        rt.center as id_center,
        rt.plant as id_plant,
        1 as id_cat,
        null as id_sub_cat,
        concat('Perdida horas') as type,
        concat('Perdida horas') as name,
        rt.cost_hours_difference as total_cost,
        0 as total_fact,
        rt.gm_objective as gm_obj,
        ( 0 - rt.cost_hours_difference) gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from jpl_prod_reg_table  as rt
        union all
        select
        (6000000000 +cte.id) as id,
        cte.start_date as date,
        dt.related_area as id_area,
        ct.related_division as id_division,
        pt.related_center as id_center,
        cte.plant_id,
        1 as id_cat,
        null as id_sub_cat,
        concat('Absentismo') as type,
        concat(hs.name) as name,
        (cte.employee_cost * (cte.x100_cost/100) * cte.hours_Day) as total_cost,
        0 as total_fact,
        pt.gm_objective as gm_obj,
        ( 0 - (cte.employee_cost * (cte.x100_cost/100) * cte.hours_Day)) as gm_total,
        0 as gm100_total,
        0 as fulfillment_gm
        from cte
        inner join jpl_prod_plant_table pt on (cte.plant_id = pt.id)
        inner join jpl_prod_center_table ct on (pt.related_center = ct.id)
        inner join jpl_prod_division_table dt on (ct.related_division = dt.id)
        inner join public.hr_holidays_status hs on (cte.holiday_status_id = hs.id)
    
        )""")


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(EstimatedGrossMargin, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        for line in res:
            if 'total_cost'in fields and 'total_fact' in fields:
                if line['total_fact'] in (0, None):
                    line['gm100_total'] = 0
                else:
                    if line['total_cost']in(0, None):
                        line['gm100_total'] = 100
                    else:
                        line['gm100_total'] = (line['total_fact']-line['total_cost'])/line['total_fact']*100
            else:
                if'gm100_total'in fields:
                    fields.remove('gm100_total')

            if 'gm100_total'in fields and 'gm_obj' in fields:
                if line['total_fact'] in (0, None):
                    line['fulfillment_gm'] = 0
                else:
                    line['fulfillment_gm'] = (line['gm100_total']-line['gm_obj'])
            else:
                if'fulfillment_gm'in fields:
                    fields.remove('fulfillment_gm')

        return res





class graphic_gm_day(models.Model):

    _name = 'jpl_prod.graphic_gm_day'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    week = fields.Float(readonly=True, store=True, ondelete='set null')
    date = fields.Float(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    totalbilling = fields.Float(readonly=True, store=True, ondelete='set null')
    totalcost = fields.Float(readonly=True, store=True, ondelete='set null')
    grossmargin = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_graphic_gm_day')
        self._cr.execute(""" CREATE VIEW jpl_prod_graphic_gm_day AS (

select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
rt.date as date,
concat(pt.name,' / ','Real') as type,
sum(rt.total_billing) as totalbilling,
sum(rt.total_cost) as totalcost,
(case when sum(rt.total_billing)<>0 then (100*((sum(rt.total_billing) - sum(rt.total_cost))/sum(rt.total_billing))) else 0.00 end) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, type,  year, week, date
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
rt.date as date,
concat(pt.name,' / ','Objetivo') as type,
0 as totalbilling,
0 as totalcost,
avg(rt.gm_objective) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, type,  year, week, date
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
rt.date as date,
concat(pt.name,' / ','Acumulado') as type,
sum(rt.total_billing) over (partition by rt.plant, extract(year from rt.date) order by rt.date) as totalbilling,
sum(rt.total_cost) over (partition by rt.plant, extract(year from rt.date) order by rt.date) as totalcost,
(case when sum(rt.total_billing) <>0 then (100*(sum(rt.total_billing) over (partition by rt.plant, extract(year from rt.date) order by rt.date)-sum(rt.total_cost) over (partition by rt.plant, extract(year from rt.date) order by rt.date))/sum(rt.total_billing) over (partition by rt.plant, extract(year from rt.date) order by rt.date)) else 0.00 end) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, type,  year, week, date, rt.total_billing,rt.total_cost, rt.plant
order by plant, date, type
         )""")


class graphic_gm_week(models.Model):

    _name = 'jpl_prod.graphic_gm_week'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    week = fields.Float(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    totalbilling = fields.Float(readonly=True, store=True, ondelete='set null')
    totalcost = fields.Float(readonly=True, store=True, ondelete='set null')
    grossmargin = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_graphic_gm_week')
        self._cr.execute(""" CREATE VIEW jpl_prod_graphic_gm_week AS (

select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','Real') as type,
sum(rt.total_billing) as totalbilling,
sum(rt.total_cost) as totalcost,
(case when sum(rt.total_billing)<>0 then (100*((sum(rt.total_billing) - sum(rt.total_cost))/sum(rt.total_billing))) else 0.00 end) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','Objetivo') as type,
0 as totalbilling,
0 as totalcost,
avg(rt.gm_objective) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
         )""")


class graphic_gm_month(models.Model):

    _name = 'jpl_prod.graphic_gm_month'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    month = fields.Float(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    totalbilling = fields.Float(readonly=True, store=True, ondelete='set null')
    totalcost = fields.Float(readonly=True, store=True, ondelete='set null')
    grossmargin = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_graphic_gm_month')
        self._cr.execute(""" CREATE VIEW jpl_prod_graphic_gm_month AS (

select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','Real') as type,
sum(rt.total_billing) as totalbilling,
sum(rt.total_cost) as totalcost,
(case when sum(rt.total_billing)<>0 then (100*((sum(rt.total_billing) - sum(rt.total_cost))/sum(rt.total_billing))) else 0.00 end) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','Objetivo') as type,
0 as totalbilling,
0 as totalcost,
avg(rt.gm_objective) as grossmargin
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
         )""")


class oee_graphic_day(models.Model):

    _name = 'jpl_prod.oee_graphic_day'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    date = fields.Date(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    resultado = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_oee_graphic_day')
        self._cr.execute(""" CREATE VIEW jpl_prod_oee_graphic_day AS (

            select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
rt.date as date,
concat(pt.name,' / ','OEE') as type,
(case when sum(rt.total_hours_presence)<>0 then (100*sum(rt.add_value_time)/sum(rt.total_hours_presence)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, date, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
rt.date as date,
concat(pt.name,' / ','Objetivo OEE') as type,
avg(rt.oee_objective) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, date, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
rt.date as date,
concat(pt.name,' / ','Limite OEE') as type,
avg(rt.oee_limit) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, date, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
rt.date as date,
concat(pt.name,' / ',' OEE Acumulada') as type,
(case when sum(rt.total_hours_presence) over (partition by rt.plant, extract(year from rt.date) order by rt.date) <> 0 then (100*sum(rt.add_value_time) over (partition by rt.plant, extract(year from rt.date) order by rt.date)/sum(rt.total_hours_presence) over (partition by rt.plant, extract(year from rt.date) order by rt.date)) else 0.00 end)  as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, date, type, rt.add_value_time, rt.plant, rt.total_hours_presence
order by date, type
         )""")

class oee_graphic_week(models.Model):

    _name = 'jpl_prod.oee_graphic_week'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    week = fields.Float(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    resultado = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_oee_graphic_week')
        self._cr.execute(""" CREATE VIEW jpl_prod_oee_graphic_week AS (

select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','OEE') as type,
(case when sum(rt.total_hours_presence)<>0 then (100*sum(rt.add_value_time)/sum(rt.total_hours_presence)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','Objetivo OEE') as type,
avg(rt.oee_objective) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','1.Disp') as type,
(case when sum(rt.total_hours_presence)<>0 then (100*sum(rt.operative_time)/sum(rt.total_hours_presence)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','2.Perf') as type,
(case when sum(rt.operative_time)<>0 then (100*sum(rt.standard_time)/sum(rt.operative_time)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant, pt.id as plant_id,
extract(year from rt.date) as year,
extract(week from rt.date) as week,
concat(pt.name,' / ','3.Quality') as type,
(case when sum(rt.standard_time)<>0 then (100*sum(rt.add_value_time)/sum(rt.standard_time)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, week, type
order by week, type
         )""")

class oee_graphic_month(models.Model):

    _name = 'jpl_prod.oee_graphic_month'
    _auto = False

    id = fields.Integer(readonly=True, store=True, ondelete='set null')
    area = fields.Text(readonly=True, store=True, ondelete='set null')
    division = fields.Text(readonly=True, store=True, ondelete='set null')
    center = fields.Text(readonly=True, store=True, ondelete='set null')
    plant = fields.Text(readonly=True, store=True, ondelete='set null')
    plant_id = fields.Many2one('jpl_prod.plant_table', string="Plant")
    year = fields.Float(readonly=True, store=True, ondelete='set null')
    month = fields.Float(readonly=True, store=True, ondelete='set null')
    type = fields.Text(readonly=True, store=True, ondelete='set null')
    resultado = fields.Float(readonly=True, store=True, ondelete='set null')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'jpl_prod_oee_graphic_month')
        self._cr.execute(""" CREATE VIEW jpl_prod_oee_graphic_month AS (

select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant,
pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','OEE') as type,
(case when sum(rt.total_hours_presence)<>0 then (100*sum(rt.add_value_time)/sum(rt.total_hours_presence)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant,
pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','Objetivo OEE') as type,
avg(rt.oee_objective) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant,
pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','1.Disp') as type,
(case when sum(rt.total_hours_presence)<>0 then (100*sum(rt.operative_time)/sum(rt.total_hours_presence)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant,
pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','2.Perf') as type,
(case when sum(rt.operative_time)<>0 then (100*sum(rt.standard_time)/sum(rt.operative_time)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
Union all
select 
1 as id,
art.name as area,
dt.name as division,
ct.name as center,
pt.name as plant,
pt.id as plant_id,
extract(year from rt.date) as year,
extract(month from rt.date) as month,
concat(pt.name,' / ','3.Quality') as type,
(case when sum(rt.standard_time)<>0 then (100*sum(rt.add_value_time)/sum(rt.standard_time)) else 0.00 end) as resultado
from jpl_prod_reg_table rt
inner join jpl_prod_area_table art on (art.id = rt.area)
inner join jpl_prod_division_table dt on (dt.id = rt.division)
inner join jpl_prod_center_table ct on (ct.id = rt.center)
inner join jpl_prod_plant_table pt on (pt.id = rt.plant)
group by art.name, dt.name, ct.name, pt.name, pt.id, year, month, type
order by month, type
         )""")
