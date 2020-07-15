from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_price(self, product_id):
        if product_id:
            product=self.env['product.product'].sudo().browse(int(product_id))
            if product:
                print(product.name, int(product.product_tmpl_id.lst_price))
                return int(product.product_tmpl_id.lst_price)
