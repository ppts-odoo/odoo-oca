from odoo import models,fields,api,_

class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    reminder_frequency = fields.Selection([
        ('one_week_before', 'One Week Before'),
        ('two_week_before', 'Two Weeks Before'),
        ('one_month_before', 'One Month Before')
        ],default='one_week_before',string="Reminder Frequency")
    

#To set values on settings to the respected model#
    def set_values(self):
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('sale.reminder_frequency', self.reminder_frequency)

#To get values from respected model #
    def get_values(self):
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            reminder_frequency=ICPSudo.get_param('sale.reminder_frequency'),
        )
        return res
