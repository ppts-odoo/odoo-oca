from datetime import datetime
from odoo import api, fields, models, _


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    @api.depends('time_ids', 'time_ids.date_end', 'time_ids.loss_type')
    def _compute_working_state(self):
        # Eliminating base function, because we no need to update Workcenter working_state.
        # working_state is useful for one user not for multiple users
        return True

    def unblock(self):
        # Eliminating base function, because we no need to block or unblock Workcenter.
        return True

                
class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'
    
    def button_block(self):
        res = super(MrpWorkcenterProductivity, self).button_block()
        # Writing the blocked user in blocked_user_ids mamy2many field
        self.env['mrp.workorder'].browse(self.env.context.get('active_id')).write({'blocked_user_ids':[(4, self.env.user.id)]})
        # Writing the blocked users log in blocked_users_logs one2many field
        mrp_workorder_id = self.env['mrp.workorder'].browse(self.env.context.get('active_id'))
        mrp_workorder_id.write({'blocked_users_logs':[(0, 0,{'workorder_id':self.workorder_id, 'loss_reason_id':self.loss_id.id, 'description':self.description, 'workcenter_id':self.workcenter_id.id})]})
        return res
