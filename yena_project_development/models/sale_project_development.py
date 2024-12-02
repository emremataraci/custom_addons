from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_sales = fields.Char(string="Project Sales")
