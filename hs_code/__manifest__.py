# -*- coding: utf-8 -*-
{
    'name': "HS Code",
    'summary': "Hs code add-on for products",
    'description': """
    Product category and customer sector specific hs code and product descriptions
    """,
    'author': "YENA Engineering, Alperen Alihan ER",
    'website': "https://www.yenaengineering.nl",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/hs_code.xml',
        'views/product.xml',
    ],
    'installable': True,
}

