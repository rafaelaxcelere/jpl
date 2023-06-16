# -*- coding: ISO-8859-1 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import mimetypes
import unicodecsv
from company import DELIMITER_DICT
from odoo.exceptions import UserError


class ImportCsvConfigSetting(models.TransientModel):
    _name = 'hr_employee_import_csv.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    hr_employee_csv_binary = fields.Binary('CSV file', related='company_id.hr_employee_csv_binary')
    change_hr_employee_csv_binary = fields.Binary('Change CSV file')
    hr_employee_csv_path = fields.Char('Path to csv file', related='company_id.hr_employee_csv_path')
    last_read_line_csv = fields.Integer('Last number line', related='company_id.last_read_line_csv', readonly=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.", related='company_id.interval_number')
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('work_days', 'Work Days'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], related='company_id.interval_type')
    separator = fields.Selection('Separator', related='company_id.separator')
    numbercall = fields.Integer(string='Number of Calls', default=1,related='company_id.numbercall',
                                help='How many times the method is called,\na negative number indicates no limit.')
    doall = fields.Boolean(string='Repeat Missed',
                           related='company_id.doall',
                           help="Specify if missed occurrences should be executed when the server restarts.")
    nextcall = fields.Datetime(string='Next Execution Date', required=True, default=fields.Datetime.now,
                               related='company_id.nextcall',
                               help="Next planned execution date for this job.")
    cron_id = fields.Many2one(related='company_id.cron_import_csv_id')
    read_line_ids = fields.One2many('hr_employee_import_csv.read_lines', 'config_id', 'CSV lines', readonly=True)

    @api.model
    def create(self, values):
        res = super(ImportCsvConfigSetting, self).create(values)
        if res.company_id.cron_import_csv_id:
            res.company_id.cron_import_csv_id.unlink()

        cron_id = self.env['ir.cron'].create(
            {'name': 'HR Employee CSV Import Schedule',
             'user_id': SUPERUSER_ID,
             'interval_number': res.interval_number,
             'interval_type': res.interval_type,
             'numbercall': res.numbercall,
             'doall': res.doall,
             'nextcall': res.nextcall,
             'model': 'res.company',
             'function': 'import_csv_data',
             'args': '()',
             }
        )
        res.company_id.cron_import_csv_id = cron_id
        return res

    @api.onchange('change_hr_employee_csv_binary')
    def onchange_hr_employee_csv_binary2(self):
        if self.change_hr_employee_csv_binary:
            self.hr_employee_csv_binary = self.change_hr_employee_csv_binary

    @api.onchange('hr_employee_csv_path')
    def onchange_path(self):
        if self.hr_employee_csv_path:
            filetype = mimetypes.guess_type(self.hr_employee_csv_path)
            if filetype and filetype[0] not in ('text/csv', 'text/plain'):
                return {'warning': {
                    'title': _('Unsupported file format'),
                    'message': _(
                        "This file '%s' is not recognised as a CSV. Please check the file and it's "
                        "extension.") % self.hr_employee_csv_path
                }}

    @api.multi
    def execute_cron(self):
        self.ensure_one()
        self.cron_id.method_direct_trigger()

    @api.multi
    def test_read(self):
        company_id = self.company_id
        try:
            f = open(
                company_id.hr_employee_csv_path, 'r')
        except IOError:
            raise UserError('Error: File does not appear to exist.')
        f.seek(0)
        reader = unicodecsv.reader(
            f,
            delimiter=DELIMITER_DICT[company_id.separator],
            quoting=unicodecsv.QUOTE_MINIMAL,
            encoding='ISO-8859-1')
        i = 0
        sap_ids = []
        lines = []
        for line in reader:
            i += 1
            if len(line) < 11:
                raise UserError(_(
                    "Error on line %d of the CSV file: this line should have "
                    "a ID SAP %s Name %s DNI %s Center address %s JPLEAN Employee Category %s "
                    "JPLEAN Employee Status(separated by a %s).") % (i, DELIMITER_DICT.get(company_id.separator),
                               DELIMITER_DICT.get(company_id.separator),
                               DELIMITER_DICT.get(company_id.separator),
                               DELIMITER_DICT.get(company_id.separator),
                               DELIMITER_DICT.get(company_id.separator),
                               company_id.separator))
            if not line[0]:
                raise UserError(_(
                    "Error on line %d of the CSV file: the line should start "
                    "with a ID SAP") % i)
            if len(line[1]) < 4:
                raise UserError("Bad DNI in line %s" % i)
            category = line[5]
            status = line[6]

            sap_ids.append(line[4])
            lines.append((0, 0,
                          {'barcode': line[4], 'name': line[0], 'identification_id': line[1],
                           'work_location': line[3], 'code_plant': line[2], 'pin': line[1][-5:-1],
                           'company_id': company_id.id, 'category': category, 'status': status,
                              'name_employee': line[7], 'surname1': line[8], 'surname2': line[9],
                              'cat_service': line[10]}
                          ))
        self.read_line_ids = lines
        return True


class ReadLines(models.TransientModel):
    _name = 'hr_employee_import_csv.read_lines'
    _description = 'Read lines csv'

    name = fields.Char()
    barcode = fields.Char()
    identification_id = fields.Char("DNI")
    work_location = fields.Char()
    code_plant = fields.Char()
    pin = fields.Char()
    category = fields.Char()
    status = fields.Char()
    config_id = fields.Many2one(comodel_name="hr_employee_import_csv.config.settings", string="Config", required=False, )
    name_employee = fields.Char()
    surname1 = fields.Char()
    surname2 = fields.Char()
    cat_service = fields.Char()