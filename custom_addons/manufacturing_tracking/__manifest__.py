{
    'name': 'Manufacturing Process Tracker',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Track manufacturing processes for products in purchase orders.',
    'description': 'This module allows you to track the manufacturing processes for each product in the purchase orders.',
    'author': 'Emre MATARACI',
    'website': 'https://www.yenaengineering.nl',
    'depends': ['base', 'purchase', 'order_flow', 'stock'],
    'data': [
        'views/inventory.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
