{
    'name': 'YENA Purchase Report',
    'version': '17.0',
    'category': 'Purchase Report',
    'summary': 'Custom purchase reports for Odoo',
    'description': """
    Reports Print
    ============
    This module provides custom print reports for various Odoo models.
    """,
    'website': 'https://www.yenaengineering.nl',
    'depends': ['base', 'purchase', 'yena_external_layout'],
    'data': [
        'reports/report_action.xml',
        'reports/report_purchase_yena.xml',
        'reports/report_rfq_yena.xml',
        'reports/report_target_rfq_yena.xml',
        'reports/report_call_off_yena.xml',
        'reports/report_ce.xml',
        'reports/report_dop.xml',
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
