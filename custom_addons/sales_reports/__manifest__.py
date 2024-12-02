{
    'name': 'YENA Sales Report',
    'version': '17.0',
    'category': 'Sales Report',
    'summary': 'Custom sales reports for Odoo',
    'description': """
    Reports Print
    ============
    This module provides custom print reports for various Odoo models.
    """,
    'website': 'https://www.yenaengineering.nl',
    'depends': ['base', 'sale', 'yena_external_layout'],
    'data': [
        'reports/report_action.xml',
        'reports/report_proposal_yena.xml',
        'reports/report_proposal_weight_yena.xml',
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
