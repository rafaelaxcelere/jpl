# -*- coding: utf-8 -*-


{
    'name': "jpl_productivity2_2",

    'summary': """
        Monitoring and Controlling processes under lean manufacturing vision.
        """,

    'description': """
        Monitoring and Controlling processes under lean manufacturing vision.
    """,

    'author': "JPL In&Co",
    'website': "http://www.jplinco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.1',
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'hr_attendance'],


    # always loaded
    'data': [
        'security/jpl_productivity_security2_2.xml',
        'security/ir.model.access.csv',
        'views/main_menu.xml',
        'views/register.xml',
        'views/configuration.xml',
        'views/reporting.xml',
        'views/economical_reporting.xml',
        'views/hr_employee.xml',
        # 'security/ir.model.access.csv',
        'reports.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
