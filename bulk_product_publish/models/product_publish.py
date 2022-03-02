from odoo import api, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def product_publish(self):
        active_ids = []
        context = dict(self._context)
        for product in self:
            active_ids.append(product.id)
        context['active_ids'] = active_ids
        return {
            'name': 'Publish/Unpublish Product',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.publish.wizard',
            'view_id': self.env.ref('bulk_product_publish.product_publish_wizard_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
        