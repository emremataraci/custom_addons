from odoo import api, fields, models

class Picking(models.Model):
    _inherit = 'stock.picking'

    project_transfer = fields.Many2many("project.project", string="Project Number", store=True)
    effective_date = fields.Date(string="Effective Date", store=True)
    arrival_date = fields.Date(related="batch_id.arrival_date", string='Arrival Date' ,store=True, readonly=False)
    logistic_company = fields.Many2one('res.partner', string='Logistic Company', domain=[('is_company', '=', True)])
    situation = fields.Selection(
        [("to_be_planned", "To Be Planned"),
         ("on_the_way", "On The Way"),
         ("arrived", "Arrived")],
        string="Situation",
        store=True,
        readonly=False
    )
    transportation_code = fields.Char(
        string="Transportation Code",
        store=True,
        readonly=False
    )
    
    def write(self, vals):
        res = super().write(vals)
        if 'batch_id' in vals:
            for record in self:
                if record.batch_id:
                    record.situation = record.batch_id.situation
        return res
        
    def _create_backorder(self):
        backorder_picking = super()._create_backorder()
        if backorder_picking:
            backorder_picking.transportation_code = '-'
        return backorder_picking