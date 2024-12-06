{
    'name': 'Production Status',
    'version': '17.0.1.0.0',
    'category': 'Custom',
    'summary': 'Production status tracking from purchase order lines',
    'description': """
Track the production status of purchase order lines
    """,
    'author': 'Emre Mataracı',
    'website': 'http://www.yenaengineering.nl',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/production_status.xml',
    ],
    'installable': True,
    'application': False,
}
