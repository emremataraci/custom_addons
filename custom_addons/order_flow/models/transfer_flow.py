from odoo import api, fields, models
from odoo.exceptions import ValidationError
import requests
import base64
from io import BytesIO
import os
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = 'stock.picking'

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
    project_transfer = fields.Many2many(
        "project.project", 
        string="Project Number", 
        store=True)


    sale_id=fields.Many2one("sale.order",string="Sale Order")
    purchase_id=fields.Many2one("purchase.order",string="Purchase Order")
    """Bu Ne?
    sequence_code = fields.Char(string='Sequence Code', related='picking_type_id.sequence_code', store=True)
    """
    """date_planned güncelliyor zaten
    @api.model
    def create(self, vals):
        self._update_scheduled_date(vals)
        return super(Picking, self).create(vals)
    
    def write(self, vals):
        self._update_scheduled_date(vals)
        return super(Picking, self).write(vals)
    """
    
    """Dropship geldiği için baştan bakılacak
    @api.model
    def _create_scheduled_activity(self):
        model_id = self.env['ir.model'].search([('model', '=', 'stock.picking')], limit=1)
        activity_type_id = self.env.ref('yena_inventory_development.activity_type_custom').id
        date_deadline = fields.Date.today() + timedelta(days=3)

        return {
            'res_model_id': model_id.id,
            'res_id': self.id,
            'activity_type_id': activity_type_id,
            'summary': 'Check Documents',
            'note': 'Lütfen TR/OUT transferi için gerekli lojistik dökümanlarının tamamlandığından emin olun.',
            'date_deadline': date_deadline,
            'user_id': self.env.user.id,
        }

    def button_validate(self):
        for record in self:
            res = super(Picking, record).button_validate()
            if record.state == 'done' and record.picking_type_id.id == 2:
                existing_activities = self.env['mail.activity'].search([
                    ('res_model_id.model', '=', 'stock.picking'),
                    ('res_id', '=', record.id),
                    ('activity_type_id', '=', self.env.ref('yena_inventory_development.activity_type_custom').id)
                ])
                if not existing_activities:
                    activity_vals = record._create_scheduled_activity()
                    self.env['mail.activity'].create(activity_vals)
        return res
    """

    """date_planned ile güncelleniyor zaten
    def _update_scheduled_date(self, vals):
        if 'scheduled_date' not in vals:
            return

        for record in self:
            picking_type = record.env['stock.picking.type'].browse(vals.get('picking_type_id', record.picking_type_id.id))

            if picking_type.sequence_code == 'IN':  # Receipts
                purchase_order = record.env['purchase.order'].search([('name', '=', record.origin)], limit=1)
                if purchase_order:
                    vals['scheduled_date'] = purchase_order.delivery_date
            elif picking_type.sequence_code == 'OUT':
                sale_order = record.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order:
                    vals['scheduled_date'] = sale_order.commitment_date
    """
    """Yerelleştirmeden dolayı değişecek
    def default_get(self, fields_list):
        defaults = super(Picking, self).default_get(fields_list)

        if self.env.user.company_id.id == 1 and self.env.context.get('default_picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id'])
            if picking_type.sequence_code == 'OUT':
                defaults['edespatch_delivery_type'] = 'edespatch'

        return defaults
    """
    
class StockMove(models.Model):
    _inherit = "stock.move"

    project_transfer = fields.Many2many(related="picking_id.project_transfer", string="Project Number")
    related_partner = fields.Many2one(related="picking_id.partner_id", string="Receive From / Delivery Adress", store=True)
    situation = fields.Selection(related="picking_id.situation", string="Situation", store=True)
    transportation_code = fields.Char(related="picking_id.transportation_code", string="Transportation Code", store=True)
    batch_id = fields.Many2one('stock.picking.batch', string='Batch', related='picking_id.batch_id', store=True, readonly=True)
    """Bulutkobi Yerelleştirme
    edespatch_delivery_type = fields.Selection(related="picking_id.edespatch_delivery_type", string="Delivery Type")
    """
    scheduled_date = fields.Datetime(related='picking_id.scheduled_date', store=True, readonly=True)
    """
    arrival_date = fields.Date(related='picking_id.arrival_date', store=True, readonly=True)
    """
    purchase_id=fields.Many2one(related='picking_id.purchase_id',string="Purchase Order")
    """Bulutkobi Yerelleştirme
    edespatch_date=fields.Datetime(related='picking_id.edespatch_date',string="Actual Departure Date")
    """
    """
    airtag_url = fields.Char(string='Airtag Link', related='picking_id.batch_id.airtag_url', store=True, readonly=True)
    
    vehicle_type_id = fields.Many2one(string='Vehicle Type', related='picking_id.batch_id.vehicle_type_id', store=True, readonly=True)
    """
    quantity_done = fields.Float(string="Quantity Done", store=True )
    sales_cost = fields.Float(string='Sales Cost', compute='_compute_sales_cost')
    effective_date = fields.Datetime(related='picking_id.date_done', store=True, readonly=True, string="Effective Date")
    weight= fields.Float(related='product_id.weight', store=True, string='Theoratical Weight')

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        for move in self.filtered(lambda m: m.state == 'done' and m.purchase_line_id):
            purchase_line = move.purchase_line_id
            product_qty = purchase_line.product_qty
            qty_received = sum(purchase_line.move_ids.filtered(lambda m: m.state == 'done').mapped('quantity_done'))

            if qty_received == product_qty:
                purchase_line.production_status = 'despatched'
            elif 0 < qty_received < product_qty:
                purchase_line.production_status = 'partially_despatched'
            elif qty_received > product_qty:
                purchase_line.production_status = 'whoops'
        return res
    

    @api.depends('state', 'product_id', 'product_uom_qty')
    def _compute_sales_cost(self):
        for move in self:
            if move.state == 'done':
                sale_order_lines = self.env['sale.order.line'].search([('product_id', '=', move.product_id.id)])
                if sale_order_lines:
                    sale_order_line = sale_order_lines[0]
                    move.sales_cost = move.product_uom_qty * sale_order_line.price_unit
                else:
                    move.sales_cost = 0.0
            else:
                move.sales_cost = 0.0
                
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        for move in self:
            available_qty = move.product_id.with_context(location=move.location_id.id).virtual_available
            if move.product_uom_qty > available_qty:
                raise ValidationError(
                    f"Stokta mevcut olan {available_qty} adetten fazla ({move.product_uom_qty}) adet gönderilemez. "
                    f"/ You cannot send more than the available stock ({available_qty}) units ({move.product_uom_qty})."
                )

            sale_order_line = move.sale_line_id
            if sale_order_line and move.product_uom_qty > sale_order_line.product_uom_qty:
                raise ValidationError(
                    f"Satış siparişindeki miktar ({sale_order_line.product_uom_qty}) ile fazla adet ({move.product_uom_qty}) gönderilemez. "
                    f"/ You cannot send more than the sales order quantity ({sale_order_line.product_uom_qty}) units ({move.product_uom_qty})."
                )
                
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    coating = fields.Selection([
        ("hot_dip_galvanized", "Hot Dip Galvanized"),
        ("electrogalvanized", "Electrogalvanized"),
        ("centrifugal_galvanise", "Centrifugal galvanise"),
        ("electrostatic_powder_coating_red", "Electrostatic powder coating Red"),
        ("epoxy_coating", "Epoxy Coating"),
        ("uncoated", "Uncoated"),
        ("electrostatic_powder_coating_black", "Electrostatic powder coating Black"),
        ("shop_primer", "Shop Primer")
    ], string="Coating")
    technical_drawing = fields.Binary('Technical Drawing', attachment=True, required=True)
    technical_drawing_filename = fields.Char('Technical Drawing Filename')
    original_filename = fields.Char('Original Filename', compute='_compute_original_filename', store=True)
    cdn_link = fields.Char('CDN Link', tracking=True)  # İzleme özelliği eklendi
    status = fields.Selection([
        ('phase1', 'Phase-1'),
        ('phase2', 'Phase-2'),
        ('phase3', 'Phase-3'),
    ], string='Phase', default='phase1', required=True, tracking=True)
    """Buna gerek var mı?
    material = fields.Many2many('product.yena_material', string="Material")
    """
    min_order_qty = fields.Char(string="Min. Order Quantity")
    """Kullanılıyor mu bilmiyorum
    manufacturing_instructions = fields.Many2many('ir.attachment', 'manufacturing_instruction_rel', 'product_id', 'attachment_id', string='Standart Operation Procedure')
    packaging_instructions = fields.Many2many('ir.attachment', 'packaging_instruction_rel', 'product_id', 'attachment_id', string='Packaging Instructions')
    packaging_images = fields.Many2many('ir.attachment', 'packaging_image_rel', 'product_id', 'attachment_id', string='Packaging Photos')
    """
    origin_country_id = fields.Many2one("res.country", string="Origin")
    """ HS_code addonuna alındı
    hs_code_description = fields.Char(string="HS Code Description", store=True)
    """
    weight= fields.Float(string="Theoratical Weight")
    """Bence gerek yok
    description_sale_en = fields.Char(string="Sale Description English", store=True)
    """
    customer_description = fields.Char(string="Customer Description", store=True)

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

    @api.model
    def default_get(self, fields_list):
        res = super(ProductTemplate, self).default_get(fields_list)
    
        # standard_price default değeri ayarlama
        if 'standard_price' not in res:
            res['standard_price'] = 1.0
    
        # MTO rota ayarlama
        mto_route_id = 1  # "MTO" rotasının ID'si
        if 'route_ids' not in res:
            res['route_ids'] = [(4, mto_route_id)]
        else:
            res['route_ids'].append((4, mto_route_id))
    
        # Varsayılan satıcı ayarlama ve satıcı bilgileri eklemek
        # Bu kısım kaldırıldı çünkü aşağıda spesifik partner_id'ler ile satırlar ekleyeceğiz
    
        # İlk ve ikinci satır için veriler, burada doğrudan belirtilen partner_id'leri kullanacağız
        lines = [
            {'partner_id': 1, 'currency_id': 1, 'company_id': 2},  # 'name' yerine modelinizin Many2one alan adını kullanın, örneğin 'partner_id'
            {'partner_id': 94654, 'currency_id': 1, 'company_id': 1},
        ]
        # Eğer seller_ids anahtarı zaten varsa bu satırları ekle, yoksa yeni bir liste oluştur
        if 'seller_ids' in res:
            res['seller_ids'].extend([(0, 0, line) for line in lines])
        else:
            res['seller_ids'] = [(0, 0, line) for line in lines]
    
        return res
    


    @api.depends('technical_drawing_filename')
    def _compute_original_filename(self):
        """Compute the original filename using the uploaded file's name, ID, timestamp, and extension."""
        for record in self:
            if record.technical_drawing_filename:
                # Dosya adını ve uzantısını ayır
                base_name, extension = os.path.splitext(record.technical_drawing_filename)
                # Geçerli tarih ve saat
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                # original_filename alanını güncelle
                record.original_filename = f"{base_name}-id={record.id}-{timestamp}{extension}"
            else:
                record.original_filename = "default_filename"

    def post_to_cdn(self):
        """Upload the technical drawing to CDN and return the URL."""
        self.ensure_one()
        if not self.technical_drawing:
            raise Exception("Technical Drawing dosyası bulunamadı.")
        
        _logger.info(f"CDN'e gönderilecek dosya adı: {self.original_filename}")
        _logger.info(f"CDN'e gönderilecek ürün adı: {self.name}")

        url = "https://portal-test.yenaengineering.nl/api/technicaldrawings"
        headers = {'Accept': 'application/json'}

        try:
            decoded_file = base64.b64decode(self.technical_drawing)
        except Exception as e:
            _logger.error(f"Dosya çözme hatası: {str(e)}")
            raise Exception(f"Dosya çözme hatası: {str(e)}")

        files = {
            'odooid': (None, str(self.id)),
            'product_name': (None, self.name),  # Doğru ürün adı gönderiliyor
            'original_filename': (None, self.original_filename),  # Doğru dosya adı gönderiliyor
            'technical_drawing': (self.original_filename, decoded_file)
        }

        # Gönderilecek verileri loglama (binary veri yerine sadece isimleri logluyoruz)
        _logger.debug(f"CDN'e gönderilen dosya verileri: odooid={self.id}, product_name={self.name}, original_filename={self.original_filename}")

        try:
            response = requests.post(url, headers=headers, files=files)
            _logger.info(f"CDN'e dosya yükleme isteği gönderildi: {url}")
            _logger.debug(f"CDN API isteği verileri: odooid={self.id}, product_name={self.name}, original_filename={self.original_filename}")
        except Exception as e:
            _logger.error(f"CDN'e dosya yükleme isteği gönderilirken hata oluştu: {str(e)}")
            raise Exception(f"CDN'e dosya yükleme isteği gönderilirken hata oluştu: {str(e)}")

        _logger.debug(f"CDN API yanıtı: {response.status_code} - {response.text}")

        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                _logger.debug(f"CDN API yanıt verisi: {response_data}")
            except ValueError:
                _logger.error("CDN yanıtı JSON formatında değil.")
                raise Exception("CDN yanıtı JSON formatında değil.")

            if response_data.get("status") == "success" and response_data.get("statusCode") == 201:
                technical_drawing_url = response_data['data'].get('technical_drawing_url')
                if technical_drawing_url:
                    _logger.info(f"CDN'den alınan URL: {technical_drawing_url}")
                    return technical_drawing_url
                else:
                    _logger.error("Yanıttan 'technical_drawing_url' bilgisi alınamadı.")
                    raise Exception("Yanıttan 'technical_drawing_url' bilgisi alınamadı.")
            else:
                _logger.error("CDN yanıtı 'success' durumunda değil.")
                raise Exception("CDN yanıtı 'success' durumunda değil.")
        else:
            _logger.error(f"CDN yüklemesi başarısız oldu. Hata kodu: {response.status_code}, Yanıt: {response.text}")
            raise Exception(f"CDN yüklemesi başarısız oldu. Hata kodu: {response.status_code}")

    def write(self, vals):
        """Override write method to upload technical drawing to CDN if updated."""
        res = super(ProductTemplate, self).write(vals)
        if 'technical_drawing' in vals or 'technical_drawing_filename' in vals:
            for record in self:
                try:
                    cdn_url = record.post_to_cdn()
                    record.cdn_link = cdn_url
                    # Chatter'a manuel mesaj gönderme kaldırıldı
                    # `cdn_link` alanındaki değişiklikler otomatik olarak izlenecek
                except Exception as e:
                    _logger.error(f"Dosya yüklenirken hata oluştu: {str(e)}")
                    raise models.ValidationError(f"Dosya yüklenirken hata oluştu: {str(e)}")
        return res

    @api.model
    def create(self, vals):
        """Override create method to upload technical drawing to CDN after creation."""
        record = super(ProductTemplate, self).create(vals)
        if record.technical_drawing and record.technical_drawing_filename:
            try:
                cdn_url = record.post_to_cdn()
                record.cdn_link = cdn_url
                # Chatter'a manuel mesaj gönderme kaldırıldı
                # `cdn_link` alanındaki değişiklikler otomatik olarak izlenecek
            except Exception as e:
                _logger.error(f"Dosya yüklenirken hata oluştu: {str(e)}")
                raise models.ValidationError(f"Dosya yüklenirken hata oluştu: {str(e)}")
        return record
    
class PackageTypes(models.Model):
    _inherit = "stock.package.type"

    gross_weight = fields.Float(string="Gross Weight")
    net_weight = fields.Float(string="Net Weight")
    stackable = fields.Boolean(string="Stackable")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    coating = fields.Selection(related="product_id.coating", string="Coating", readonly=True)
    unit_weight = fields.Float(related="product_id.weight", string="Unit Weight", readonly=True)
    product_category = fields.Many2one('product.category', related="product_id.categ_id", string="Product Category")
    product_type = fields.Selection(related='product_id.detailed_type', string='Product Type', store=True)
    totalweight = fields.Float(string="Total Weight", readonly=True, compute="_compute_total_weight")
    pricekg = fields.Float(string="KG Price", readonly=True, compute="_compute_pricekg")

    @api.depends('unit_weight', 'product_qty')
    def _compute_total_weight(self):
        for record in self:
            record.totalweight = record.unit_weight * record.product_qty

    @api.depends('price_subtotal', 'totalweight')
    def _compute_pricekg(self):
        for record in self:
            if record.totalweight != 0:
                record.pricekg = record.price_subtotal / record.totalweight
            else:
                record.pricekg = 0

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_type = fields.Selection(related='product_id.detailed_type', string='Product Type', store=True)
    product_category = fields.Many2one('product.category', related="product_id.categ_id", string="Product Category")
    totalweight = fields.Float(string='Total Weight', compute='_compute_total_weight', store=True, readonly=True)
    coating = fields.Selection(related="product_id.coating", string="Coating", readonly=True)
    pricekg = fields.Float(compute='_compute_pricekg', string='KG Price', readonly=True, store=True)
    unit_weight = fields.Float(related="product_id.weight", string="Unit Weight", readonly=True)

    @api.depends('unit_weight', 'product_uom_qty')
    def _compute_total_weight(self):
        for record in self:
            record.totalweight = record.unit_weight * record.product_uom_qty

    @api.depends('price_subtotal', 'totalweight')
    def _compute_pricekg(self):
        for record in self:
            if record.totalweight != 0:
                record.pricekg = record.price_subtotal / record.totalweight
            else:
                record.pricekg = 0