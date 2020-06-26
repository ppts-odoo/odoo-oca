from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from itertools import chain


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    product_category = fields.Many2many('product.category', string="Product Category")
    terms = fields.Html(string="Terms and Conditions")
    set_price = fields.Float(string="Set Price")
    
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', ondelete='cascade',
        help="Specify a template if this rule only applies to one product template. Keep empty otherwise.")
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete='cascade',
        help="Specify a product if this rule only applies to one product. Keep empty otherwise.")
    categ_id = fields.Many2one(
        'product.category', 'Product Category', ondelete='cascade',
        help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise.")
    min_quantity = fields.Integer(
        'Min. Quantity', default=0,
        help="For the rule to apply, bought/sold quantity must be greater "
             "than or equal to the minimum quantity specified in this field.\n"
             "Expressed in the default unit of measure of the product.")
    applied_on = fields.Selection([
        ('3_global', 'Global'),
        ('2_product_category', ' Product Category'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='3_global', required=True,
        help='Pricelist Item applicable on selected option')
    sequence = fields.Integer(
        'Sequence', default=5, required=True,
        help="Gives the order in which the pricelist items will be checked. The evaluation gives highest priority to lowest sequence and stops as soon as a matching item is found.")
    base = fields.Selection([
        ('list_price', 'Public Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist')], "Based on",
        default='list_price', required=True,
        help='Base price for computation.\n'
             'Public Price: The base price will be the Sale/public Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')
    base_pricelist_id = fields.Many2one('product.pricelist', 'Other Pricelist')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', index=True, ondelete='cascade')
    price_surcharge = fields.Float(
        'Price Surcharge', digits=dp.get_precision('Product Price'),
        help='Specify the fixed amount to add or substract(if negative) to the amount calculated with the discount.')
    price_discount = fields.Float('Price Discount', default=0, digits=(16, 2))
    price_round = fields.Float(
        'Price Rounding', digits=dp.get_precision('Product Price'),
        help="Sets the price so that it is a multiple of this value.\n"
             "Rounding is applied after the discount and before the surcharge.\n"
             "To have prices that end in 9.99, set rounding 10, surcharge -0.01")
    price_min_margin = fields.Float(
        'Min. Price Margin', digits=dp.get_precision('Product Price'),
        help='Specify the minimum amount of margin over the base price.')
    price_max_margin = fields.Float(
        'Max. Price Margin', digits=dp.get_precision('Product Price'),
        help='Specify the maximum amount of margin over the base price.')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
        readonly=True, store=True)
    
    date_start = fields.Date('Start Date', help="Starting date for the pricelist item validation")
    date_end = fields.Date('End Date', help="Ending valid for the pricelist item validation")
    compute_price = fields.Selection([
        ('fixed', 'Fix Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula')], index=True, default='fixed')
    
    fixed_price = fields.Float('Fixed Price', digits=dp.get_precision('Product Price'))
    percent_price = fields.Float('Percentage Price')
    price = fields.Char(
        'Price', compute='_get_pricelist_item_name_price',
        help="Explicit rule name for this pricelist line.")
    
    @api.constrains('base_pricelist_id', 'pricelist_id', 'base')
    def _check_recursion(self):
        if any(item.base == 'pricelist' and item.pricelist_id and item.pricelist_id == item.base_pricelist_id for item in self):
            raise ValidationError(_('Error! You cannot assign the Main Pricelist as Other Pricelist in PriceList Item!'))
        return True
    
    @api.constrains('price_min_margin', 'price_max_margin')
    def _check_margin(self):
        if any(item.price_min_margin > item.price_max_margin for item in self):
            raise ValidationError(_('Error! The minimum margin should be lower than the maximum margin.'))
        return True
    
    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        if self.compute_price != 'fixed':
            self.fixed_price = 0.0
        if self.compute_price != 'percentage':
            self.percent_price = 0.0
        if self.compute_price != 'formula':
            self.update({
                'price_discount': 0.0,
                'price_surcharge': 0.0,
                'price_round': 0.0,
                'price_min_margin': 0.0,
                'price_max_margin': 0.0,
            })
    
    def import_products(self):
        for line in self.item_ids:
            line.unlink()
        for obj in self:
            if obj.applied_on == '2_product_category':
                for rec_new in obj.product_category:
                    rec_pricelist_cat = obj.item_ids
                    items_list = []
                    for items in obj.item_ids:
                        if items.categ_id not in items_list:
                            items_list.append(items.categ_id)
                    if rec_new not in items_list:
                        self.env['product.pricelist.item'].create({
                                'applied_on':obj.applied_on,
                                'categ_id':rec_new.id,
                                'min_quantity':obj.min_quantity,
                                'compute_price':obj.compute_price,
                                'date_start':obj.date_start,
                                'date_end':obj.date_end,
                                'fixed_price':obj.fixed_price,
                                'base':obj.base,
                                'price_discount':obj.price_discount,
                                'base_pricelist_id':obj.base_pricelist_id.id,
                                'percent_price':obj.percent_price,
                                'price_surcharge':obj.price_surcharge,
                                'price_round':obj.price_round,
                                'price_min_margin':obj.price_min_margin,
                                'price_max_margin':obj.price_max_margin,
                                'pricelist_id':obj.id,
                                })
            elif obj.applied_on == '1_product':
                
                res = self.env['product.template'].search([('categ_id', 'in', obj.product_category.ids), ('pricelist_active', '=', True)])
                if res:
                    for i in res:
                        values = {
                            'applied_on':obj.applied_on,
                            'min_quantity':obj.min_quantity,
                            'compute_price':obj.compute_price,
                            'product_tmpl_id':i.id,
                            'date_start':obj.date_start,
                            'date_end':obj.date_end,
                            'fixed_price':obj.fixed_price,
                            'base':obj.base,
                            'price_discount':obj.price_discount,
                            'percent_price':obj.percent_price,
                            'price_surcharge':obj.price_surcharge,
                            'price_round':obj.price_round,
                            'price_min_margin':obj.price_min_margin,
                            'price_max_margin':obj.price_max_margin,
                            'base_pricelist_id':obj.base_pricelist_id.id,
                            'pricelist_id':obj.id,
                            }
                          
                        self.env['product.pricelist.item'].create(values)

            elif obj.applied_on == '0_product_variant':
                res = self.env['product.product'].search([('categ_id', 'in', obj.product_category.ids), ('pricelist_active', '=', True)])
                if res:
                    for i in res:
                        values = {
                            'applied_on':obj.applied_on,
                            'min_quantity':obj.min_quantity,
                            'compute_price':obj.compute_price,
                            'product_id':i.id,
                            'date_start':obj.date_start,
                            'date_end':obj.date_end,
                            'fixed_price':obj.fixed_price,
                            'base':obj.base,
                            'price_discount':obj.price_discount,
                            'percent_price':obj.percent_price,
                            'price_surcharge':obj.price_surcharge,
                            'price_round':obj.price_round,
                            'price_min_margin':obj.price_min_margin,
                            'price_max_margin':obj.price_max_margin,
                            'base_pricelist_id':obj.base_pricelist_id.id,
                            'pricelist_id':obj.id,
                        }
                 
                        self.env['product.pricelist.item'].create(values)
            else:
                values = {
                    'applied_on':obj.applied_on,
                    'min_quantity':obj.min_quantity,
                    'compute_price':obj.compute_price,
                    'date_start':obj.date_start,
                    'date_end':obj.date_end,
                    'fixed_price':obj.fixed_price,
                    'base':obj.base,
                    'price_discount':obj.price_discount,
                    'percent_price':obj.percent_price,
                    'price_surcharge':obj.price_surcharge,
                    'price_round':obj.price_round,
                    'price_min_margin':obj.price_min_margin,
                    'price_max_margin':obj.price_max_margin,
                    'base_pricelist_id':obj.base_pricelist_id.id,
                    'pricelist_id':obj.id,
                }
         
                self.env['product.pricelist.item'].create(values)

        
    def refresh_pricelists(self):
        res_obj = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.id)])
        if res_obj:
            for i in res_obj:
                if self.compute_price == 'fixed':
                    i.fixed_price = self.fixed_price
                elif self.compute_price == 'percentage':
                    i.percent_price = self.percent_price
                elif self.compute_price == 'formula':
                    i.price_discount = self.price_discount
                    i.price_surcharge = self.price_surcharge
                    i.base = self.base
                    i.price_round = self.price_round
                    i.price_min_margin = self.price_min_margin
                    i.price_max_margin = self.price_max_margin
                    i.base_pricelist_id = self.base_pricelist_id.id

             
class ProductTemplate(models.Model):
    _inherit = 'product.template'
   
    pricelist_active = fields.Boolean('Include Pricelist', default=True, help="Specify if the product can be selected in pricelist or not.")

    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    pricelist_active = fields.Boolean('Include Pricelist', related="product_tmpl_id.pricelist_active", default=True, help="Specify if the product can be selected in pricelist or not.")


class PricelistLineitem(models.Model):
    _inherit = 'product.pricelist.item'
    _order = "sequence"
    
    sequence = fields.Integer(string='Sequence')
