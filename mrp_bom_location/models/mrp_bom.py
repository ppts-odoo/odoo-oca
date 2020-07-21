# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models,_
from odoo.exceptions import Warning

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.location',
    )

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if (self.picking_type_id and
                self.picking_type_id.default_location_src_id):
            self.location_id = self.picking_type_id.default_location_src_id


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    location_id = fields.Many2one(
        related='bom_id.location_id',
        store=True,
    )
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    stock_location_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Location',related='company_id.stock_location_ids',readonly=False,
    )
    stock_warning = fields.Boolean("Enable Stock Warning",related='company_id.stock_warning',readonly=False)
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    stock_location_ids = fields.Many2many(
            string='Location',
            comodel_name='stock.location',
        ) 
    stock_warning = fields.Boolean("Enable Stock Warning")
    
    
class MrpProduction(models.Model):
    _inherit = 'mrp.production'
        
    @api.multi
    def open_produce_product(self):
        if self.company_id.stock_warning == True:
            for line_ids in self.move_raw_ids:
                if line_ids.product_uom_qty != line_ids.reserved_availability:
                    raise Warning(_('There is no reserved Quantities for' + line_ids.product_id.name))

        self.ensure_one()
        action = self.env.ref('mrp.act_mrp_product_produce').read()[0]
        return action
    
    @api.multi
    def button_plan(self):
        """ Create work orders. And probably do stuff, like things. """
        if self.company_id.stock_warning == True:
            for line_ids in self.move_raw_ids:
                if line_ids.product_uom_qty != line_ids.reserved_availability:
                    raise Warning(_('There is no reserved Quantities for' + line_ids.product_id.name))
                
        orders_to_plan = self.filtered(lambda order: order.routing_id and order.state == 'confirmed')
        for order in orders_to_plan:
            quantity = order.product_uom_id._compute_quantity(order.product_qty, order.bom_id.product_uom_id) / order.bom_id.product_qty
            boms, lines = order.bom_id.explode(order.product_id, quantity, picking_type=order.bom_id.picking_type_id)
            order._generate_workorders(boms)
        return orders_to_plan.write({'state': 'planned'})
   
