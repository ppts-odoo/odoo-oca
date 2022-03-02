from odoo import api, fields, models,_


class ResUsers(models.Model):
    _inherit = "res.users"

    is_salesperson = fields.Boolean("Is a Salesperson")

