import base64
import os
import requests
from odoo import models, fields, api, tools
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template with Technical Drawing and CDN Link'

    technical_drawing = fields.Binary('Technical Drawing', attachment=True, required=True)
    technical_drawing_filename = fields.Char('Technical Drawing Filename')
    original_filename = fields.Char('Original Filename', compute='_compute_original_filename', store=True)
    cdn_link = fields.Char('CDN Link', tracking=True)  # İzleme özelliği eklendi
    status = fields.Selection([
        ('phase1', 'Phase-1'),
        ('phase2', 'Phase-2'),
        ('phase3', 'Phase-3'),
    ], string='Durum', default='phase1', required=True, tracking=True)

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
