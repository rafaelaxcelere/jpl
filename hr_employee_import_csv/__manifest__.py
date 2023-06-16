# -*- coding: ISO-8859-1 -*-
{
    'name': "hr_employee_import_csv",

    'summary': """
        Import data from a csv and generate employees.
        """,

    'description': """
        Import data from a csv and generate employees.
    """,

    "author": "ASOLUTIONS",
    "website": "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Human Resources",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance'],

    # always loaded
    'data': [
        'views/import_res_config_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
