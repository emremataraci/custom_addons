{
    'name': 'Batch Transfer Extension',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Extends Batch Transfer with additional fields',
    'author': 'Emre Mataracı',
    'website': 'http://yourwebsite.com',
    'depends': ['stock', 'project', 'purchase', 'contacts', 'stock_picking_batch'],
    'data': [
        'views/batch_transfer_view.xml',
        'security/ir.model.access.csv',
        'data/email_template.xml'
    ],
    'installable': True,
    'auto_install': False,
}
