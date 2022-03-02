from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    blocked_user_ids = fields.Many2many('res.users', 'workcenter_blocked_user_rel',
        'workcenter_id', 'user_id', 'Blocked User')
    is_user_blocked = fields.Boolean(
        'Is Current User Blocked', compute='_compute_is_user_working',
        help="Technical field indicating whether the current user is blocked or not. ")
    blocked_users_logs = fields.One2many('mrp.workorder.blocked.users.logs', 'workorder_id', 'Users Blocked Logs')
   

    def _compute_is_user_working(self):
        """ Checks whether the current user is working or blocked """
        for order in self:
            existing_ids = [val.id for val in order.blocked_user_ids]
            if self.env.user.id in existing_ids:
                order.is_user_blocked = True
                order.is_user_working = False
            elif order.time_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                order.is_user_blocked = False
                order.is_user_working = True
            else:
                order.is_user_blocked = False
                order.is_user_working = False

    def button_unblock(self):
        # Eliminating base function, because we no need to block or unblock Workcenter.
        for order in self:
            existing_ids = [val.id for val in order.blocked_user_ids]
            # if current user exists in existing_block_ids, it will remove current user from list
            if self.env.uid in existing_ids:
                existing_ids.remove(self.env.uid)
            order.write({'blocked_user_ids': [(6,0,existing_ids)]})
            # Updating end_date and duration for blocked_users_logs
            blockline_obj = self.env['mrp.workorder.blocked.users.logs']
            domain = [('workorder_id', '=', self.id), ('block_end_date', '=', False), ('user_id', '=', self.env.user.id)]
            for blockline in blockline_obj.search(domain, limit= 1):
                wo = blockline.workorder_id
                diff = fields.Datetime.from_string(fields.Datetime.now()) - fields.Datetime.from_string(blockline.block_start_date)
                blocked_duration = round(diff.total_seconds() / 60.0, 2)
                if blockline.loss_type != 'productive':
                    blockline.write({'block_end_date': fields.Datetime.now(), 'duration': blocked_duration})
                else:
                    maxdate = fields.Datetime.from_string(blockline.block_start_date) + relativedelta(minutes=wo.duration_expected - wo.duration)
                    enddate = datetime.now()
                    if maxdate > enddate:
                        blockline.write({'block_end_date': enddate, 'duration': blocked_duration})
                    else:
                        blockline.write({'block_end_date': maxdate, 'duration': blocked_duration})
                        loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
                        if not len(loss_id):
                            raise UserError(_("You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class MrpWorkorderBlockedUsersLogs(models.Model):
    _name = 'mrp.workorder.blocked.users.logs'
    _description = "Mrp Workorder Blocked Users Logs"

    workorder_id = fields.Many2one('mrp.workorder', "Work Order")
    workcenter_id = fields.Many2one('mrp.workcenter', "Work Center", store=True)
    loss_reason_id = fields.Many2one('mrp.workcenter.productivity.loss', "Loss Reason", ondelete='restrict', required=True)
    loss_type = fields.Selection("Effectiveness", related='loss_reason_id.loss_type', store=True)
    block_start_date = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    block_end_date = fields.Datetime('End Date',default=False)
    duration = fields.Float('Duration', store=True, digits=(16, 2))
    description = fields.Text('Description')
    user_id = fields.Many2one('res.users', "User", default=lambda self: self.env.uid)


