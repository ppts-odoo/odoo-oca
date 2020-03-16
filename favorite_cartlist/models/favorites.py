# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


# // Favorites
class Favorites(models.Model):
    _name = "website.favorites"
    _description = "Favorites"
    
    name = fields.Char("Name", required=True)
    favorites_ids = fields.One2many('favorites.list', 'favorite_id', string="favorites")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)

 
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique!'),
    ]

# // Favorites
class FavoritesList(models.Model):
    _name = "favorites.list"
    
    favorite_id = fields.Many2one('website.favorites', string="Favorites")
    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float("Quantity")
