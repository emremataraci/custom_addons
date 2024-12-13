from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    processes = fields.Many2many(
        'manufacturing.process',
        string="Processes",
        help="Select the processes related to the product"
    )

class ManufacturingProcess(models.Model):
    _name = 'manufacturing.process'
    _description = 'Manufacturing Process'

    name = fields.Char(
        string="Process Name", required=True, help="Name of the manufacturing process"
    )
