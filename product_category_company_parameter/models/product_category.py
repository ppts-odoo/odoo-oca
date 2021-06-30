from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"
      
    asset_category_pro_id = fields.Many2one("account.asset.category", string="Asset Category",company_dependent=True)

