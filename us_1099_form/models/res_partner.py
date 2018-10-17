from odoo import api, fields, models,_

class Partner(models.Model):
    _inherit = "res.partner"

    x_1099 = fields.Boolean("1099")
