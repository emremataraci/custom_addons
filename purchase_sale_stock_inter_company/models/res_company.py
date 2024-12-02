from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse for Sale Orders",
        help=(
            "Default warehouse to set on Sale Orders that will be created "
            "based on Purchase Orders made to this company."
        ),
    )
