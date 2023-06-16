# -*- coding: utf-8 -*-
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.tools.sql import drop_view_if_exists


class HRAttendanceTask(models.Model):
    _name = 'hr.attendance.task'
    _auto = False
    _table = 'hr_attendance_task_view'

    name = fields.Char(string="Name", size=100, readonly=1)
    id_activity = fields.Integer('Activity Id', readonly=1)
    type = fields.Selection(string="Type",
                            selection=[('process', 'Process'),
                                       ('inefficiency', 'Inefficiency'),
                                       ('hours_process', 'HourProcess'),
                                       ],
                            required=False, readonly=1)
    active_employee_id = fields.Many2one(
        'hr.employee',
        compute='compute_active_employee_id'
    )
    active_employee_id_attendance_state = fields.Selection(
        related='active_employee_id.attendance_state'
    )
    show = fields.Boolean(string="Active", readonly=1)

    @api.one
    def compute_active_employee_id(self):
        self.active_employee_id = self._context.get('employee_id', False)

    related_plant = fields.Many2one(
        'jpl_prod.plant_table',
        ondelete='set null', string="Related Plant",
        index=False, required=True
     )

    id_cat = fields.Many2one('jpl_prod.process_category_table', ondelete='set null', string="Category",
                             index=False, required=True)
    id_sub_cat = fields.Many2one('jpl_prod.process_sub_category_table', ondelete='set null', string="Subcategory",
                                 index=False)
    is_eight_task = fields.Boolean(store=True)

    # eight_task = fields.Many2many('hr.attendance.task', compute='compute_eight_task', )
    #
    # @api.multi
    # def compute_eight_task(self):
    #     # ob_task = self.env['hr.attendance.task']
    #     entities = self.search([], order='id_activity desc', limit=8)
    #     for r in self:
    #         if r.id in entities.ids:
    #             r.is_eight_task = True

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'hr_attendance_task_view')
        self._cr.execute("""
               create or replace view hr_attendance_task_view as (
                  SELECT
                      cast((concat('1', id)) AS INTEGER) AS id,
                      id                                 AS id_activity,
                      name,
                      'process'                          AS type,
                      active                             AS show,
                      related_plant,
                      id_cat,
                      id_sub_cat,
                     CASE
                WHEN process.id IN (
                    SELECT id_activity
                    FROM (
                        SELECT id_activity, ROW_NUMBER() OVER (ORDER BY activity_count DESC) AS row_num
                        FROM (
                            SELECT id_activity, COUNT(*) AS activity_count
                            FROM hr_attendance
                            GROUP BY id_activity
                        ) AS activity_counts
                    ) AS top_activities
                    WHERE row_num <= 8
                ) THEN true
                ELSE false
            END AS is_eight_task
                    FROM jpl_prod_process_table AS process
                    UNION SELECT
                            cast((concat('2', id)) AS INTEGER) AS id,
                            id                                 AS id_activity,
                            name,
                            'hours_process'                     AS type,
                            active                             AS show,
                            related_plant,
                            id_cat,
                            id_sub_cat,
                            false              AS is_eight_task
                          FROM jpl_prod_hourprocess_table AS hours
                    UNION SELECT
                            cast((concat('3', id)) AS INTEGER) AS id,
                            id                                 AS id_activity,
                            name,
                            'inefficiency'                    AS type,
                            active                             AS show,
                            related_plant,
                             id_cat,
                            id_sub_cat,
                            false              AS is_eight_task
                          FROM jpl_prod_inef_table
               )""")

        # WHERE
        # active = TRUE and active = False

    def get_all_attendance_task(self):
        attendances_task = self.search([])
        task_list = [{'id': each.id, 'value': each.name, 'label': each.name} for
                     each in attendances_task]
        return task_list






