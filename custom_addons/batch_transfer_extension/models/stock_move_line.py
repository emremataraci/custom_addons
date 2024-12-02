from odoo import api, fields, models

class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    project_ids = fields.Many2many('project.project', string='Projects', compute='_compute_project_transfer', store=True)

    @api.depends('picking_id.project_transfer')
    def _compute_project_transfer(self):
        for record in self:
            record.project_ids = record.picking_id.project_transfer
            