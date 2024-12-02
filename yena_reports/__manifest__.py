{
    'name': 'YENA Report',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Custom reports for Odoo',
    'description': """
    Reports Print
    ============
    This module provides custom print reports for various Odoo models.
    """,
    'author': 'Emre MATARACI',
    'website': 'https://www.yenaengineering.nl',
    'depends': ['base', 'purchase'],
    'data': [
        'reports/deneme.xml',
        'reports/report_action.xml',
        'reports/report_external_layout_alperen.xml',
        'reports/report_purchase_alperen.xml',
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
