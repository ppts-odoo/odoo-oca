from odoo import fields,models,api, _

class PromotionSetup(models.Model):
    _name = 'promotion.setup' 
    
    
    name = fields.Char(string="Offer Name",required=True)
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")
    text_to_display = fields.Text("Description")
    url = fields.Char("URL")
    active = fields.Boolean("Active")
    bg_color = fields.Char("Banner Background Color")
    text_color = fields.Char("Banner Text Color")
    btn_color = fields.Char("Button Background Color")
    btn_txt_color = fields.Char("Button Text Color")





