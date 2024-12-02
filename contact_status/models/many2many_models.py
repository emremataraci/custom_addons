from odoo import models, fields

class TypeOfMaterial(models.Model):
    _name = "type.material"

    name = fields.Char(string="Name")