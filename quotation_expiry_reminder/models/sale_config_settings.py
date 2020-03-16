from odoo import models,fields,api,_

class SaleConfiguration(models.TransientModel):
    _name = 'sale.config.settings'
    _inherit = ['sale.config.settings']
    
    reminder_frequency = fields.Selection([
        ('one_week_before', 'One Week Before'),
        ('two_week_before', 'Two Weeks Before'),
        ('one_month_before', 'One Month Before')
        ],default='one_week_before')
    
#To set values on settings to the respected model#
    @api.multi
    def set_quotation_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'reminder_frequency', self.reminder_frequency)
        
#To get values from settings to the respected model#
    @api.model
    def _default_get_values(self):
        return self.env['ir.values'].get_default('sale.config.settings', 'reminder_frequency')

