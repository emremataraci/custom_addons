{
    'name': 'YENA BATCH Report',
    'version': '17.0',
    'category': 'Purchase Report',
    'summary': 'Custom purchase reports for Odoo',
    'description': """
    Reports Print
    ============
    This module provides custom print reports for various Odoo models.
    """,
    'website': 'https://www.yenaengineering.nl',
    'depends': ['stock', 'project', 'purchase', 'contacts', 'batch_transfer_extension', 'stock_picking_batch'],
    'data': [
        'reports/report_action.xml',
        'reports/report_ce.xml',
        'reports/report_dop.xml',
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
