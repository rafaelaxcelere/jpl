# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models, _
from dateutil import relativedelta
from datetime import datetime

import hashlib
import logging

logger = logging.getLogger(__name__)

from odoo.exceptions import UserError

try:
    import unicodecsv
except ImportError:
    logger.debug('Cannot import unicodecsv')

DELIMITER = [('colon', ':'), ('semicolon', ';'), ('comma', ',')]
DELIMITER_DICT = {x: y for x, y in DELIMITER}


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_employee_csv_path = fields.Char('Path to csv file')
    hr_employee_csv_binary = fields.Binary('CSV file')
    last_read_line_csv = fields.Integer('Last number line')
    interval_number = fields.Integer(default=-1, help="Repeat every x.")
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('work_days', 'Work Days'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')],
                                     default='months')
    checksum_dir = fields.Char('Last checksum csv dir')
    separator = fields.Selection(DELIMITER,
                                 default='comma', string='Separator')
    numbercall = fields.Integer(string='Number of Calls', default=1,
                                help='How many times the method is called,\na negative number indicates no limit.')
    doall = fields.Boolean(string='Repeat Missed',
                           help="Specify if missed occurrences should be executed when the server restarts.")
    nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                               help="Next planned execution date for this job.")
    cron_import_csv_id = fields.Many2one('ir.cron', 'Cron to execute import data')

    @api.multi
    def _get_checksum(self):
        self.ensure_one()
        """Compute a sha1 digest of file contents."""
        m = hashlib.sha1()
        # hash filename so empty files influence the hash
        m.update(self.hr_employee_csv_path.encode('ISO-8859-1'))
        # hash file content
        with open(self.hr_employee_csv_path, 'rb') as f:
            m.update(f.read())
        return m.hexdigest()

    @api.multi
    def has_changed(self):
        self.ensure_one()
        return self.checksum_dir != self._get_checksum()

    @api.model
    def import_csv_data(self):
        """Import data from SAP csv and generate employees"""
        company_ids = self.search([('cron_import_csv_id', '!=', False)])
        for company_id in company_ids:
            logger.info('Import data from CSV ...')
            with open(company_id.hr_employee_csv_path, 'r') as f:

                f.seek(0)
                reader = unicodecsv.reader(
                    f,
                    delimiter=DELIMITER_DICT[company_id.separator],
                    quoting=unicodecsv.QUOTE_MINIMAL,
                    encoding='ISO-8859-1')
                i = 0
                sap_ids = []
                for line in reader:
                    logger.debug('csv line %d: %s', i, line)
                    i += 1
                    if len(line) < 11:
                        raise UserError(_(
                            "Error on line %d of the CSV file: this line should have "
                            "a ID SAP, Name, DNI, Center address, PIN,"
                            " JPLEAN Employee Category and JPLEAN Employee Status   separated by a "
                            "%s.") % (i, company_id.separator))
                    if not line[0]:
                        raise UserError(_(
                            "Error on line %d of the CSV file: the line should start "
                            "with a EMPLOYEE NAME") % i)
                    if len(line[1]) < 4:
                        raise UserError("Bad DNI in line %s" % i)
                    sap_ids.append(line[4])

                    category = line[5]
                    status = line[6]

                    values = {'barcode': line[4], 'name': line[0], 'identification_id': line[1],
                              'work_location': line[3], 'code_plant': line[2], 'pin': line[1][-5:-1],
                              'company_id': company_id.id, 'category': category, 'status': status,
                              'name_employee': line[7], 'surname1': line[8], 'surname2': line[9],
                              'cat_service': line[10]}

                    self.env['hr.employee'].crud(values)
                    self._cr.commit()
                company_id.last_read_line_csv = i

                # Archived employee not present in CSV

                if sap_ids:
                    now_utc_minus3 = datetime.utcnow() - relativedelta.relativedelta(seconds=604800)
                    res = self.env['hr.employee'].search([('barcode', 'not in', sap_ids),
                                                          ('create_date', '<', now_utc_minus3.strftime('%Y-%m-%d %H:%M:%S')),
                                                          ('active', '=', True)]).write({'active': False})

        return True


