from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_transfer = fields.Char(string="Project Transfer")
