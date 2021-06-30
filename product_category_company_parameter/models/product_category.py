from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"
      
    asset_category_pro_id = fields.Many2one("account.asset.category", string="Asset Category",company_dependent=True)

    def view_wizard(self):
        active_ids = self.env.context.get('active_ids',[])
        categ_id = self.env['product.category'].search([('id','in',active_ids)])
        return {
            'name':"Account Properties",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'prodect.category.company',
            'target': 'new',
            }
