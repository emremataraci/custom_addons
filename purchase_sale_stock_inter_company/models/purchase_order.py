# Copyright 2023 Odoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from typing import Dict, Any


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_sale_order_data(
        self,
        name: str,
        partner,
        dest_company,
        direct_delivery_address,
    ) -> Dict[str, Any]:
        new_order = super()._prepare_sale_order_data(
            name, partner, dest_company, direct_delivery_address
        )
        delivery_address = (
            direct_delivery_address
            or self.picking_type_id.warehouse_id.partner_id
            or False
        )
        if delivery_address:
            new_order.update({"partner_shipping_id": delivery_address.id})
        warehouse = (
            dest_company.warehouse_id.company_id == dest_company
            and dest_company.warehouse_id
            or False
        )
        if warehouse:
            new_order.update({"warehouse_id": warehouse.id})
        return new_order
