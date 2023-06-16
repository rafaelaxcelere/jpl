# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models


import logging
logger = logging.getLogger(__name__)
try:
    import unicodecsv
except ImportError:
    logger.debug('Cannot import unicodecsv')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    name_employee = fields.Char("Nombre empleado")
    surname1 = fields.Char("Apellido 1")
    surname2 = fields.Char("Apellido 2")
    cat_service = fields.Char("Categoria Servicio")

    @api.model
    def crud(self, values):
        result = False
        category_env = self.env['jpl_prod.employee_category']
        status_env = self.env['jpl_prod.employee_status']

        employee_to_update = self.with_context(active_test=False).search([
            ('barcode', '=', values.get('barcode')), ('company_id', '=', values.get('company_id'))], limit=1)

        category_id = category_env.search([('name', '=', values.get('category'))], limit=1) or\
                      category_env.create({'name': values.get('category')})

        status_id = status_env.search([('name', '=', values.get('status'))], limit=1) or\
                    status_env.create({'name': values.get('status')})
        del values['category']
        del values['status']
        if status_id and category_id:
            values.update({
                'employee_category': category_id.id,
                'employee_status': status_id.id
            })

            #Si el empleado aparece en el CSV se activa nuevamente
            inactive_ids = employee_to_update.filtered(lambda x: not x.active)
            if inactive_ids:
                inactive_ids.write({'active': True})

            if not employee_to_update:
               result = self.create(values)

            elif employee_to_update.name != values.get('name') or employee_to_update.identification_id != values.get(
                    'identification_id') or employee_to_update.work_location != values.get(
                    'work_location') or employee_to_update.pin != values.get('pin') or employee_to_update.name_employee != values.get('name_employee') or \
                    employee_to_update.code_plant != values.get(
                    'code_plant'):
               result = employee_to_update.write(values)
        return result




