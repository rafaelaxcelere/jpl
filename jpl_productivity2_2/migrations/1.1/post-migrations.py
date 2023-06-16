# -*- coding: utf-8 -*-

from openerp import api, SUPERUSER_ID
import logging
logger = logging.getLogger(__name__)


def compute_many2many(env):
    reg_table_ids = env['jpl_prod.process_reg_table'].search([])
    logger.info(u"Calculando campos many2many del modelo jpl_prod.process_reg_table que pasan a ser store=True")
    reg_table_ids._compute_possible_prod_waste_reg_table_ids()
    reg_table_ids._compute_possible_task_register_table_ids()
    logger.info(u"Fin de procedimiento")


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        context = {'post_migration': version}
        env = api.Environment(cr, SUPERUSER_ID, context)
        compute_many2many(env)
