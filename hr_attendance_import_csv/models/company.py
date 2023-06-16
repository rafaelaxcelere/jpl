# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models, _
import hashlib
import logging

logger = logging.getLogger(__name__)

from odoo.exceptions import UserError

try:
    import csv
except ImportError:
    logger.debug('Cannot import csv')

DELIMITER = [('colon', ':'), ('semicolon', ';'), ('comma', ',')]
DELIMITER_DICT = {x: y for x, y in DELIMITER}


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_attendance_csv_path = fields.Char('Path to csv file')
    hr_attendance_csv_binary = fields.Binary('CSV file')
    att_last_read_line_csv = fields.Integer('Last number line')
    att_interval_number = fields.Integer(default=-1, help="Repeat every x.")
    att_interval_type = fields.Selection([('minutes', 'Minutes'),
                                          ('hours', 'Hours'),
                                          ('work_days', 'Work Days'),
                                          ('days', 'Days'),
                                          ('weeks', 'Weeks'),
                                          ('months', 'Months')],
                                         default='months')
    att_checksum_dir = fields.Char('Last checksum csv dir')
    att_separator = fields.Selection(DELIMITER,
                                     default='comma', string='Separator')
    att_numbercall = fields.Integer(string='Number of Calls', default=1,
                                    help='How many times the method is called,\na negative number indicates no limit.')
    att_doall = fields.Boolean(string='Repeat Missed',
                               help="Specify if missed occurrences should be executed when the server restarts.")
    att_nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                                   help="Next planned execution date for this job.")
    att_cron_import_csv_id = fields.Many2one('ir.cron', 'Cron to execute import data')

    @api.multi
    def _get_checksum(self):
        self.ensure_one()
        """Compute a sha1 digest of file contents."""
        m = hashlib.sha1()
        # hash filename so empty files influence the hash
        m.update(self.hr_attendance_csv_path.encode('ISO-8859-1'))
        # hash file content
        with open(self.hr_attendance_csv_path, 'rb') as f:
            m.update(f.read())
        return m.hexdigest()

    @api.multi
    def has_changed(self):
        self.ensure_one()
        return self.att_checksum_dir != self._get_checksum()

    @api.model
    def _cron_load_attendance_from_file(self):
        """Import data from csv and generate attendances"""
        company_ids = self.search([('att_cron_import_csv_id', '!=', False)])
        logger.info('Import attendance data from CSV ...')
        for company_id in company_ids:
            with open(company_id.hr_attendance_csv_path, 'r') as f:
                f.seek(0)
                reader = csv.reader(f, delimiter=DELIMITER_DICT[company_id.att_separator], quotechar='|')
                i = 0
                for line in reader:
                    logger.debug('csv line %d: %s', i, line)
                    i += 1
                    if len(line) < 5:
                        raise UserError(_(
                            "Error on line %d of the CSV file: this line should have "
                            "a ID, Name, Check in, Check out and Attendance task separated by a %s.") %
                                        (i, company_id.att_separator))
                    if not line[0]:
                        raise UserError(_(
                            "Error on line %d of the CSV file: the line should start "
                            "with a ID") % i)
                    if not line[2]:
                        raise UserError(_(
                            "Error on line %d of the CSV file: the line should have "
                            "a Check in data") % i)

                    values= {'barcode': line[0], 'name': line[1], 'check_in': line[2],
                             'check_out': line[3], 'attendance_task': line[4],
                             'company_id': company_id.id}

                    self.env['hr.attendance'].crud(values)
                    self._cr.commit()
                    company_id.att_last_read_line_csv = i

        return True
