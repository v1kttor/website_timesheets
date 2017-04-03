# -*- coding: utf-8 -*-
{
    'name': 'website_timesheets',

    'summary': 'website timesheets',
    'description': 'Website Timesheets',
    'author': 'Viktoras',
    'website': "http://www.yourcompany.com",
    'category': 'website',
    'version': '10.0.0.1',
    'depends': ['base', 'invoice_time_sheet_lines'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
