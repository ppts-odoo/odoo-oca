from odoo import api, fields, models

class ProductPublishWizard(models.TransientModel):
    _name = "product.publish.wizard"
    
    state = fields.Selection([('publish', 'Publish'), ('unpublish', 'Unpublish')], string='Website', required=True,default='unpublish')

    @api.multi
    def publishing_state(self):  
        self.ensure_one()        
        context = dict(self._context or {})       
        active_ids = context.get('active_ids', []) 
        for rec in active_ids:           
            if rec:
                product_record = self.env['product.template'].browse(rec)
                if self.state == 'unpublish':
                    product_record.write({'website_published': False})
                elif self.state == 'publish':
                    product_record.write({'website_published': True})
            
        return {'type' : 'ir.actions.act_window_close'}
