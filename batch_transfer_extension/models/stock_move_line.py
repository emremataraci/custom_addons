from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_transfer = fields.Many2many('project.project', string='Project Transfer')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    project_ids = fields.Many2many('project.project', string='Projects', compute='_compute_project_transfer', store=True)
    @api.depends('picking_id.project_transfer')
    def _compute_project_transfer(self):
        for record in self:
            if record.picking_id.project_transfer:
                record.project_ids = [(6, 0, record.picking_id.project_transfer.ids)]
            else:
                record.project_ids = [(5,)]
