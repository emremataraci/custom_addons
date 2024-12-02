from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contact_id = fields.Many2one('res.partner', string='Contact Person', store=True)
    sharepoint_url=fields.Char(string="Share Point URL")

    bid_time=fields.Char(string="Bid Time")
    quo_date=fields.Date(string="C-Quotation Date")
    rfq_date=fields.Date(string="C-RFQ Date")
    delivery_date=fields.Char(string="C-Delivery Date (Text)")

    rfq_reference=fields.Char(string="RFQ Reference", store=True)

    customer_reference=fields.Char(string="Customer Reference No", store=True)
    project_sales=fields.Many2one("project.project",string="Project Number", store=True)

    """Bulutkobi yerelleştirme
    document_numbers = fields.Char(string='Document Numbers', compute='_compute_document_numbers')
    """
    """TRANSFER DEVELOPMENTININ İÇERİSİNE ALINACAK
    transportation_codes = fields.Char(string="Transportation Codes", compute='_compute_transportation_codes')
    """
    """Effective Date satış içerisinde var transfer gerçekleşince gözüküyor bu fonksiyona gerek yok
    date_done_list = fields.Char(string="Effective Date", compute='_compute_date_done_list')
    """
    """YERELLEŞTİRMEDEN DOLAYI DEĞİŞECEK
    edespatch_date_list = fields.Char(string="EDespatch-Date", compute='_compute_edespatch_date_list') 
    """
    invoice_report = fields.Selection([
        ("fullyinvoiced", "Fully Invoiced"),
        ("partiallyinvoice", "Partially Invoiced"),
        ("nothinginvoiced", "Nothing Invoiced")
    ], string="Invoice Report", compute='_compute_invoice_report', store=True)
    
    """YERELLEŞTİRMEDEN DOLAYI DEĞİŞECEK
    def _compute_edespatch_date_list(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            if pickings:
                edespatch_dates_str = ', '.join(picking.edespatch_date.strftime("%Y-%m-%d") for picking in pickings if picking.edespatch_date)
                order.edespatch_date_list = edespatch_dates_str
            else:
                order.edespatch_date_list = ''
    """
    @api.onchange('commitment_date')
    def _onchange_commitment_date(self):
        for line in self.order_line:
            line.product_delivery_date = self.commitment_date
            
    def action_quotation_sent(self):
        res = super(SaleOrder, self).action_quotation_sent()
        for record in self:
            record.write({
                'quo_date': fields.Date.today(),
            })

        return res
        
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.contact_id = False
        return {'domain': {'contact_id': [('parent_id', '=', self.partner_id.id), ('type', '=', 'contact')]}}
        
    """BENCE GEREKSİZ GEREKLİYSE REPORT ID DEĞİŞECEK(Başta koyma laf ederlerse ekle)
    def print_proposal_form(self):
        # id'si 2298 olan raporu indir
        return self.env.ref('__export__.ir_act_report_xml_2298_852ac486').report_action(self)
    """    
    
    @api.depends('order_line.product_uom_qty', 'order_line.qty_invoiced')
    def _compute_invoice_report(self):
        for order in self:
            # Varsayılan olarak "nothinginvoiced" varsayalım
            invoice_status = "nothinginvoiced"
            partially_invoiced = False
            fully_invoiced = True

            for line in order.order_line:
                if line.qty_invoiced > 0:
                    if line.qty_invoiced < line.product_uom_qty:
                        partially_invoiced = True
                        fully_invoiced = False
                        break  # En az bir satır kısmen faturalandırıldıysa döngüden çık
                    else:
                        # Bu satır tamamen faturalandırıldı, döngü devam eder
                        invoice_status = "fullyinvoiced"
                else:
                    fully_invoiced = False  # Eğer qty_invoiced 0 ise tamamen faturalandırılmamıştır

            if partially_invoiced:
                invoice_status = "partiallyinvoice"
            elif fully_invoiced:
                invoice_status = "fullyinvoiced"
            else:
                invoice_status = "nothinginvoiced"

            order.invoice_report = invoice_status
            
    """DOCUMENT NUMBER DİYE BİR ŞEY YOK        
    def _compute_document_numbers(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            if pickings:
                document_numbers = [picking.document_number for picking in pickings if picking.document_number]
                document_numbers_str = ', '.join(document_numbers)
                order.document_numbers = document_numbers_str
            else:
                order.document_numbers = ''
    """

    """TRANSFER DEVELOPMENTININ İÇERİSİNE ALINACAK
    def _compute_transportation_codes(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            if pickings:
                unique_transportation_codes = {picking.transportation_code for picking in pickings if picking.transportation_code}
                transportation_codes_str = ', '.join(unique_transportation_codes)
                order.transportation_codes = transportation_codes_str
            else:
                order.transportation_codes = ''
    """
    """Satınalmacılar mı girecek muhasebe mi karar verilecek(Muhasebede ayarlanacak gibi)
    Kaldırılıyor
    def tax_button(self):
        tax_to_clear_ids = [
            self.env.ref('__export__.account_tax_125_7615b3b3').id,
            self.env.ref('__export__.account_tax_208_e1b8c54a').id
        ]
        for order in self:
            if order.tax_selection.id in tax_to_clear_ids:
                for line in order.order_line:
                    line.tax_id = [(5, 0, 0)]
            else:
                for line in order.order_line:
                    line.tax_id = [(6, 0, [order.tax_selection.id])]
    """ 
    """Butona elveda
    def create_project_button(self):
        if not self.customer_reference:
            return

        project_vals = {
            'name': self.name + '-' + self.customer_reference,
            'partner_id': self.partner_id.id,
            'company_id': 2,  # `id` değerini kullanın
        }
        project = self.env['project.project'].create(project_vals)

        # Proje oluşturulduktan sonra analitik hesap ID'yi al
        analytic_account_id = project.analytic_account_id.id if project.analytic_account_id else None

        # Son olarak, satışa analitik hesabı ve proje ID'yi ekleyin.
        self.write({
            'analytic_account_id': analytic_account_id,
            'project_sales': project.id,
            'company_id':2,
        })               
    """    
    """Effective Date satış içerisinde var transfer gerçekleşince gözüküyor bu fonksiyona gerek yok 
    def _compute_date_done_list(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            if pickings:
                date_dones = [picking.date_done.strftime("%Y-%m-%d") for picking in pickings if picking.date_done]
                date_dones_str = ', '.join(date_dones)
                order.date_done_list = date_dones_str
            else:
                order.date_done_list = ''
    """
    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', False)
        if company_id == 1:
            return super().create(vals)
        # customer_reference'ın rfq_reference'a kopyalandığını kontrol edin.
        if 'customer_reference' in vals and vals['customer_reference']:
            vals['rfq_reference'] = vals['customer_reference']
        # rfq_date'i bugünün tarihi ile doldurun.
        vals['rfq_date'] = fields.Date.today()
        record = super().create(vals)
        if not record.customer_reference:
            return record
        # satış oluşturulduktan sonra bir proje oluştur.
        project_vals = {
            'name': record.name + '-' + record.customer_reference,
            'partner_id': record.partner_id.id,
            'company_id': 2,
        }
        project = self.env['project.project'].create(project_vals)
        # Proje oluşturulduktan sonra analitik hesap ID'yi al
        analytic_account_id = project.analytic_account_id.id if project.analytic_account_id else None
        # Son olarak, satışa analitik hesabı ve proje ID'yi ekleyin.
        record.write({
            'analytic_account_id': analytic_account_id,
            'project_sales': project.id,
            'company_id': 2,
        })
        return record

    def action_confirm(self):
        # C-Delivery Date kontrolü
        if not self.commitment_date:
            raise UserError('The C-Delivery Date is mandatory! Please add this date and try again.')
            
        """DROPSHİP OLACAĞI VE MTO Full kullanılacağı için bu aşamaya gerek yok
        # company_id 1 ise, standart onay işlemi yapılır ve özel işlemlerden kaçınılır
        if self.company_id.id == 1:
            res = super(SaleOrder, self).action_confirm()

            for order in self:
                # İlgili transfer emirlerini bul ve güncelle
                delivery_orders = self.env['stock.picking'].search([('origin', '=', order.name)])
                for delivery_order in delivery_orders:
                    delivery_order.write({
                        'project_transfer': [(6, 0, order.project_sales.ids)],
                    })
                return res
        """
        # Diğer durumlarda, öncelikle standart onay işlemi yapılır
        res = super(SaleOrder, self).action_confirm()
    
        current_user = self.env.user  # Şu anki kullanıcıyı al
        incoterm = self.env['account.incoterms'].browse(10)
    
        for order in self:
            purchase_orders = self.env['purchase.order'].search([('origin', '=', order.name)])
            for purchase_order in purchase_orders:
                purchase_order.write({
                    'user_id': current_user.id,
                    'customer_reference': order.customer_reference,
                    'project_purchase': order.project_sales.id,
                    'incoterm_id': incoterm.id
                })
    
                # İlişkili tüm satın alma siparişi satırlarını sil
                purchase_order.order_line.unlink()
    
                # Yeni satın alma siparişi satırlarını oluştur
                for so_line in order.order_line:
                    new_price_unit = so_line.price_unit * 0.8
                    po_line = purchase_order.order_line.create({
                        'order_id': purchase_order.id,
                        'product_id': so_line.product_id.id,
                        'product_qty': so_line.product_uom_qty,
                        'product_uom': so_line.product_uom.id,
                        'price_unit': new_price_unit,
                        'name': so_line.name,
                        'date_planned': purchase_order.date_order,
                        'account_analytic_id': order.analytic_account_id.id,
                        'sale_line_id': so_line.id,  # Satış siparişi satırını bağla
                    })
                    # Satış siparişi satırına geri bağlantı oluştur
                    so_line.purchase_line_ids = [(4, po_line.id)]
        """
            # İlişkili tüm teslimat emirlerini bul
            delivery_orders = self.env['stock.picking'].search([('origin', '=', order.name)])
            # İlişkili tüm teslimat emirlerini güncelle
            for delivery_order in delivery_orders:
                delivery_order.write({
                    'project_transfer': [(6, 0, order.project_sales.ids)],
                })
        """
        # Eğer customer_reference değiştiyse analitik hesap ve proje adını güncelle
        if self.rfq_reference != self.customer_reference:
            project = self.project_sales
            project.write({
                'name': self.name + '-' + self.customer_reference
            })
            analytic_account = self.analytic_account_id
            analytic_account.write({
                'name': project.name
            })
    
        return res
    
    @api.onchange('project_sales')
    def _onchange_project_sales(self):
        if self.project_sales and self.project_sales.analytic_account_id:
            self.analytic_account_id = self.project_sales.analytic_account_id.id

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_delivery_date = fields.Date(string="Product Delivery Date")