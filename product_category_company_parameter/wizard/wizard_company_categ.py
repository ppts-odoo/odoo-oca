from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductCategoryCompany(models.TransientModel):
    _name = 'prodect.category.company'

    income_account_id = fields.Many2one('account.account', 'Income Account', required=False, ondelete="cascade", index=2)
    expense_account_id = fields.Many2one('account.account', 'Expense Account', required=False, ondelete="cascade",index=2)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id, readonly=True)
    include_asset = fields.Boolean('Include Asset Category')
    asset_category_id = fields.Many2one('account.asset.category', 'Category')

    @api.multi
    def confirm(self):
        context = dict(self._context)
       
        context['income_account_id'] = self.income_account_id.id  
        context['expense_account_id'] = self.expense_account_id.id
        prod_obj = self.env['product.template']
        
        
        rows = self.env['product.category'].browse(self.env.context.get('active_ids'))
        for rec in  rows:
            prod_sr = prod_obj.search([('categ_id', '=', rec.id)])
            if prod_sr:
                for loop in prod_sr:
                    loop.asset_category_id = self.asset_category_id.id
            
            if self.income_account_id:
                if rec.property_account_income_categ_id:                   
                    return {
                        'name': ('Account Entry Existing'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'product.category.account.entries',
                        'view_id': self.env.ref('product_category_company_parameter.product_account_entries_warnig_form').id,
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'target': 'new'
                    }
                else:
                    rec.write({'property_account_income_categ_id':self.income_account_id})

            if self.expense_account_id:
                if rec.property_account_expense_categ_id:                    
                    return {
                        'name': ('Account Entry Existing'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'product.category.account.entries',
                        'view_id': self.env.ref('product_category_company_parameter.product_account_entries_warnig_form').id,
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'target': 'new'
                    }
                else:
                    rec.write({'property_account_expense_categ_id':self.expense_account_id})
            if not rec.asset_category_pro_id:   
                rec.write({'asset_category_pro_id':self.asset_category_id.id})  
        return True


class ProductAccountEntries(models.TransientModel):
    _name = 'product.category.account.entries' 
    
    def continue_to_new_product_entry(self):        
            income_account_id = self.env.context.get('income_account_id')      
            expense_account_id = self.env.context.get('expense_account_id')  

            rows = self.env['product.category'].browse(self.env.context.get('active_ids'))
            for rec in  rows:        
                if income_account_id is not False:
                    rec.write({'property_account_income_categ_id':income_account_id})
                if expense_account_id is not False:
                    rec.write({'property_account_expense_categ_id':expense_account_id})
        
# ProductCategoryCompany()