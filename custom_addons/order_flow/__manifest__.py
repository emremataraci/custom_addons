# -*- coding: utf-8 -*-
{
    'name': "Order Flow",
    'summary': "All order flow from sales to purchase",
    'description': """
    All order flow from sales to purchase
    """,
    'author': "YENA Engineering, Alperen Alihan ER",
    'website': "https://www.yenaengineering.nl",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'purchase', 'sale', 'sale_crm', 'sale_management', 'product', 'stock', 'barcodes', 'digest', 'account', 'delivery'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_order_flow.xml',
        'views/purchase_order_flow.xml',
        'views/inventory_development.xml'
    ],
    'installable': True,
}