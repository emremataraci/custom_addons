{
    'name': 'Price History with purchase',
    'version': '1.0',
    'summary': 'Adds Sale and Purchase Price History to Sale',
    'sequence': 10,
    'description': """Bu modül, envanter ürünlerinin satış ve alış fiyat geçmişini takip etmek için Sales modülü altına bir 'Price History' sayfası ekler. Kullanıcılar bu sayfada ürünlerin fiyat değişimlerini detaylı bir şekilde görebilirler.""",
    'category': 'Inventory',
    'author': 'Selçuk Atav',
    'website': 'https://www.yenaengineering.nl',
    'license': 'AGPL-3',
    'depends': ['base', 'stock','sale','purchase'],
    'data': [
        'views/price_history.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
}