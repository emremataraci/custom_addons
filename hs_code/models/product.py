from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'    
    
    hs_code = fields.Char(string="HS Code", store=True)
    hs_code_description = fields.Char(string="HS Code Description", store=True)
    customer = fields.Many2one('res.partner', domain=[('is_company', '=', True)], string="Customer")

    @api.model
    def create(self, values):
        record = super(ProductTemplate, self).create(values)
        record._update_hs_code()
        return record

    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if 'categ_id' in values or 'customer' in values:
            self._update_hs_code()
        return res

    def _update_hs_code(self):
        for record in self:
            if record.categ_id and record.customer and record.customer.industry_id:
                hs_code_record = self.env['yena.hscode'].search([
                    ('category', '=', record.categ_id.id),
                    ('industry', '=', record.customer.industry_id.id),
                ], limit=1)
                if hs_code_record:
                    record.hs_code = hs_code_record.name
                    record.description = hs_code_record.product_description
                    record.description_sale = hs_code_record.customs_description_en
                    record.description_purchase = hs_code_record.customs_description_tr
                    record.hs_code_description = hs_code_record.example_description
                else:
                    record.hs_code = False
                    record.description = ''
                    record.description_sale = ''
                    record.description_purchase = ''
                    record.hs_code_description = ''