from odoo import models,fields,api,_

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    reorder_qty_mail_to = fields.Char('Reorder Qty Mail To')

#To set values on settings to the respected model#
    @api.multi
    def set_quotation_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'base.config.settings', 'reorder_qty_mail_to', self.reorder_qty_mail_to)
        
#To get values from settings to the respected model#
    @api.model
    def _default_get_values(self):
        return self.env['ir.values'].get_default('base.config.settings', 'reorder_qty_mail_to')