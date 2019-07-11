from odoo import api, fields, models, _


class assign_followers_settings(models.Model):
    _name = 'assign.followers.settings'
    _description = 'Settings for Assign and Remove followers to a Record'

    name = fields.Char('Name', size=128)
    model_id = fields.Many2one('ir.model', 'Model')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True,
                                        help="Sidebar action to make this template available on records "
                                        "of the related document model")
    ref_ir_value = fields.Many2one('ir.model.data', 'Sidebar Button', readonly=True,
                                       help="Sidebar button to open the sidebar action")
    
    @api.multi
    def create_action(self):
        action_obj = self.env['ir.actions.act_window'].sudo()
 
        for template in self:
            src_obj = template.model_id.model
            model_data_id = self.env['ir.model.data'].get_object_reference('assign_followers', 'view_assign_followers')[1]         
            button_name = _('Assign/Unassign Followers')
           
# create follower action
            action_id = action_obj.create({
                  'name': button_name,
                  'type': 'ir.actions.act_window',
                  'res_model': 'assign.followers',
                  'src_model': src_obj,
                  'view_type': 'form',
                  'context': "{}",
                  'view_mode':'form,tree',
                  'view_id': model_data_id,
                  'target': 'new',
                  'binding_model_id': template.model_id.id,
                'auto_refresh':1,
                     
            })
           
            template.write({
                    'ref_ir_act_window': action_id.id,
                 })
        return True
    
    @api.multi
    def unlink(self):
        # action template remove 
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        return super(assign_followers_settings, self).unlink()
    
class assign_followers(models.Model):
    _name = 'assign.followers'
    _description = 'Assign and Unassign Followers to Record'
   
    record_followers_ids = fields.Many2many('res.partner', 'record_followers_rel', 'record_id', 'partner_id', 'Followers')
    
    @api.multi
    def assign_followers(self):
        context = self._context
        if context is None:
            context = {}
        if context.get('active_model'):
            # Current model name
            model_obj = self.env[context['active_model']]
            model_follower_obj = self.env['mail.followers']
            followers_ids = self.record_followers_ids.ids
            if context.get('active_ids'):    
                # get values from current active_ids
                for value in model_obj.search([('id', 'in', context['active_ids'])]):
                    existing_followers_id = followers_to_assign = []
                    existing_followers_id = [val.partner_id.id for val in value.message_follower_ids]
                    # check existing message followers and assigned followers
                    followers_to_assign = list(set(followers_ids) - set(existing_followers_id))
                    for val_loop in followers_to_assign:
                        model_follower_obj.create({'partner_id': val_loop, 'res_model': context['active_model'], 'res_id': value.id})                        
        return True
    
    @api.multi
    def update_followers(self):
        context = self._context
        if context is None:
            context = {}
        if context.get('active_model'):
            model_obj = self.env[context['active_model']]
            model_follower_obj = self.env['mail.followers']
            active_model_id = model_obj.search([('id', 'in', self._context.get('active_ids'))])
            followers_ids = [val.id for val in self.record_followers_ids]
            for line in active_model_id:  
                    # check existing message followers and record_followers_ids
                    followers_to_unassign = list(set(followers_ids))
                    for val_loop in followers_to_unassign:
                        model_follower_obj.search([('partner_id','=', val_loop),('res_model','=', self._context.get('active_model')),( 'res_id','=', line.id)]).unlink()
                                          
        return True
    
        
           
              
