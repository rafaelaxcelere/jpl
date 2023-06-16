# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import mimetypes
import csv
from company import DELIMITER_DICT
from odoo.exceptions import UserError


class AttImportCsvConfigSetting(models.TransientModel):
    _name = 'hr_attendance_import_csv.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    hr_attendance_csv_binary = fields.Binary('CSV file', related='company_id.hr_attendance_csv_binary')
    change_hr_attendance_csv_binary = fields.Binary('Change CSV file')
    hr_attendance_csv_path = fields.Char('Path to csv file', related='company_id.hr_attendance_csv_path')
    last_read_line_csv = fields.Integer('Last number line', related='company_id.att_last_read_line_csv', readonly=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.", related='company_id.att_interval_number')
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('work_days', 'Work Days'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], related='company_id.att_interval_type')
    separator = fields.Selection('Separator', related='company_id.att_separator')
    numbercall = fields.Integer(string='Number of Calls', default=-1, related='company_id.att_numbercall',
                                help='How many times the method is called,\na negative number indicates no limit.')
    doall = fields.Boolean(string='Repeat Missed',
                           related='company_id.att_doall',
                           help="Specify if missed occurrences should be executed when the server restarts.")
    nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                               related='company_id.att_nextcall',
                               help="Next planned execution date for this job.")
    cron_id = fields.Many2one(related='company_id.att_cron_import_csv_id')
    read_line_ids = fields.One2many('hr_attendance_import_csv.read_lines', 'config_id', 'CSV lines', readonly=True)

    @api.model
    def create(self, values):
        res = super(AttImportCsvConfigSetting, self).create(values)
        if res.company_id.att_cron_import_csv_id:
            res.company_id.att_cron_import_csv_id.unlink()

        cron_id = self.env['ir.cron'].create(
            {'name': 'HR Attendance CSV Import Schedule',
             'user_id': SUPERUSER_ID,
             'interval_number': res.interval_number,
             'interval_type': res.interval_type,
             'numbercall': res.numbercall,
             'doall': res.doall,
             'nextcall': res.nextcall,
             'model': 'res.company',
             'function': '_cron_load_attendance_from_file',
             'args': '()',
             }
        )
        res.company_id.att_cron_import_csv_id = cron_id
        return res

    @api.onchange('change_hr_attendance_csv_binary')
    def onchange_hr_attendance_csv_binary(self):
        if self.change_hr_attendance_csv_binary:
            self.hr_attendance_csv_binary = self.change_hr_attendance_csv_binary

    @api.onchange('hr_attendance_csv_path')
    def onchange_path(self):
        pass
        # if self.hr_attendance_csv_path:
        #     filetype = mimetypes.guess_type(self.hr_attendance_csv_path)
        #     if filetype and filetype[0] not in ('text/csv', 'text/plain'):
        #         return {'warning': {
        #             'title': _('Unsupported file format'),
        #             'message': _(
        #                 "This file '%s' is not recognised as a CSV. Please check the file and it's "
        #                 "extension.") % self.hr_attendance_csv_path
        #         }}

    @api.multi
    def execute_cron(self):
        self.ensure_one()
        self.cron_id.method_direct_trigger()

    @api.multi
    def test_read(self):
        if self.read_line_ids:
            self.read_line_ids.unlink()
        company_id = self.company_id
        delimiter = DELIMITER_DICT[company_id.att_separator]
        try:
            f = open(company_id.hr_attendance_csv_path, 'r')
        except IOError:
            raise UserError('Error: File does not appear to exist.')
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter, quotechar='|')
        i = 0
        lines = []
        for line in reader:
            i += 1
            if len(line) < 5:
                raise UserError(_(
                    "Error on line %d of the CSV file: this line should have "
                    "a ID %s Name %s Check in %s Check out %s Attendance task "
                    "(separated by a %s).") % (i, delimiter, delimiter, delimiter, delimiter,
                                               company_id.att_separator))
            if not line[0]:
                raise UserError(_(
                    "Error on line %d of the CSV file: the line should start "
                    "with a ID") % i)
            if not line[2]:
                raise UserError(_(
                    "Error on line %d of the CSV file: the line should have "
                    "a Check in data") % i)
            lines.append((0, 0,
                          {'barcode': line[0], 'name': line[1], 'check_in': line[2],
                           'check_out': line[3], 'attendance_task': line[4],
                           'company_id': company_id.id}
                          ))
        self.read_line_ids = lines
        return True


class AttReadLines(models.TransientModel):
    _name = 'hr_attendance_import_csv.read_lines'
    _description = 'Read lines csv'

    barcode = fields.Char()
    name = fields.Char()
    check_in = fields.Char()
    check_out = fields.Char()
    attendance_task = fields.Char()
    config_id = fields.Many2one(comodel_name="hr_attendance_import_csv.config.settings", string="Config",
                                required=False)
