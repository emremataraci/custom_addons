{
    'name': 'YENA External Layout',
    'version': '17.0',
    'category': 'Report',
    'summary': 'Custom external layout for Odoo',
    'description': """
    Reports Print
    ============
    This module provides custom print reports for various Odoo models.
    """,
    'website': 'https://www.yenaengineering.nl',
    'depends': ['base'],
    'data': [
        'reports/report_external_layout_yena.xml',
        'reports/report_external_layout_without_footer.xml',
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
