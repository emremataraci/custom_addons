{
    'name': 'Reports Print',
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
        'reports/reports_print.external_layout_yena.xml',
        'reports/reports_print.imzasız_external_layout_yena.xml',
        'reports/reports_print.external_layout_yena2.xml',
        'reports/purchase/report_purchase_actions.xml',
        'reports/purchase/report_purchase_order.xml',
        'reports/purchase/report_purchase_order_cagri_mektubu.xml',
        'reports/purchase/report_purchase_rfq.xml',
        'reports/purchase/report_purchase_rfq_hedef.xml',
        'reports/purchase/report_purchase_dop.xml',
        'reports/purchase/report_purchase_ce.xml',
        'reports/purchase/report_purchase_alperen.xml',
        'reports/sale/report_sale_actions.xml',
        'reports/sale/report_sale_proposal_form.xml',
        'reports/sale/report_sale_confirmation_of_order.xml',
        'reports/sale/report_sale_proposal_form_weight_price.xml',
        'reports/sale/report_sale_pro_forma_invoice.xml',
        'reports/sale/report_sale_ce.xml',
        'reports/sale/report_sale_dop.xml'
        ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
