from odoo import models,fields,api,_

class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    reorder_qty_mail_to = fields.Char('Reorder Qty Mail To')

#To set values on settings to the respected model#
#     @api.multi
    def set_values(self):
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('purchase.reorder_qty_mail_to', self.reorder_qty_mail_to)

#To get values from respected model #
    @api.model
    def get_values(self):
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            reorder_qty_mail_to=ICPSudo.get_param('purchase.reorder_qty_mail_to'),
        )
        return res
