
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductCategory(models.Model):
    _inherit = "product.category"
      
    asset_category_pro_id = fields.Many2one("account.asset.category", string="Asset Category",company_dependent=True)
    
