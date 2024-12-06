from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Additional Fields
    delivered_qty = fields.Float(string="Delivered Quantity")
    delivery_date = fields.Date(string="Delivery Date")
    project_purchase = fields.Many2one(
        'project.project',
        related='order_id.project_purchase',
        string='Project Purchase',
        store=True,
        readonly=True
    )

    material_procurement = fields.Float(string="Material Procurement (%)")
    cutting = fields.Float(string="Cutting (%)")
    bending = fields.Float(string="Bending (%)")
    welding = fields.Float(string="Welding (%)")
    soldering = fields.Float(string="Soldering (%)")
    machining = fields.Float(string="Machining (%)")
    coating = fields.Float(string="Coating (%)")
    assembly = fields.Float(string="Assembly (%)")
    packaging = fields.Float(string="Packaging (%)")

    ready = fields.Float(string="Ready (%)", compute="_compute_ready", store=False)

    # Sequence Number: Computed based on create_date to avoid dependency on 'id'
    sequence_number = fields.Integer(string="Sequence No", compute="_compute_sequence_number", store=False)

    @api.depends(
        'material_procurement', 'cutting', 'bending', 'welding', 
        'soldering', 'machining', 'coating', 'assembly', 'packaging'
    )
    def _compute_ready(self):
        for rec in self:
            values = [
                rec.material_procurement or 0.0,
                rec.cutting or 0.0,
                rec.bending or 0.0,
                rec.welding or 0.0,
                rec.soldering or 0.0,
                rec.machining or 0.0,
                rec.coating or 0.0,
                rec.assembly or 0.0,
                rec.packaging or 0.0
            ]
            total = sum(values)
            count = len(values)
            rec.ready = total / count if count else 0.0

    @api.depends('order_id', 'create_date')  # 'id' bağımlılığı kaldırıldı
    def _compute_sequence_number(self):
        # Tüm purchase.order.line kayıtlarını create_date'e göre sırala
        all_lines = self.env['purchase.order.line'].search([]).sorted(key=lambda r: r.create_date)
        for rec in self:
            try:
                rec.sequence_number = all_lines.ids.index(rec.id) + 1
            except ValueError:
                rec.sequence_number = 0
