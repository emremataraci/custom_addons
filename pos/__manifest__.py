{
    'name': 'POS Redirect on Login',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Redirects users to POS UI on login',
    'description': 'This module redirects users to the POS UI screen upon login.',
    'author': 'Your Name',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_view.xml',
    ],
    'installable': True,
    'application': False,
}