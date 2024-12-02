from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'


    unknown_company = fields.Boolean(string="I don't know her/his company")

    # 'type' 'driver' ise 'unknown_company' True yapar
    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'driver':
            self.unknown_company = True
        else:
            self.unknown_company = False

    # Kullanıcının Phone, Mobile veya Email alanlarından en az birini doldurması istenir!
    @api.constrains('phone', 'mobile', 'email')
    def _check_contact_info(self):
        for record in self:
            if not record.phone and not record.mobile and not record.email:
                raise ValidationError(_('You must fill at least one of the following: Phone, Mobile or Email!'))
    
    # Kaydın ülkesi Türkiye olarak seçilmişse dil 'tr_TR', değilse 'en_US' yapar
    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id.id == 224:
            self.lang = 'tr_TR'
        else:
            self.lang = 'en_US'
            
# Müşterinin stock move hareketlerini gösteren bir pencere açar.
# Inventory ile beraber çalıştığından dolayı inventory_development içerisinde contact_development.py dosyasında yazmak daha yararlı olacaktır.
    def action_view_stock_moves(self):
        self.ensure_one()

        domain = [('customer', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'domain': domain,
            'context': {'default_customer': self.id},
        }
