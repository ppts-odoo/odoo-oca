from odoo import models , fields , _
from datetime import date, datetime
import calendar
import logging
_logger = logging.getLogger(__name__)

class Mailscheduler(models.Model):
    _name = "mail.scheduler"

    name = fields.Char("Name", required=True)
    template_id = fields.Many2one('mail.template', "E-mail Template", required=True)
    active = fields.Boolean("Active", default=True)

    def action_cron(self):
        reminder_ids = self.env['mail.scheduler'].search([])
        today_date = date.today()
        # To separate the year, month and day from the current date.
        last_date = datetime(today_date.year, today_date.month, today_date.day)
        # To get last day of  current month.
        month_last_day = calendar.monthrange(last_date.year, last_date.month)[1]
        if month_last_day == today_date.day:
            for rec in reminder_ids:
                rec.template_id.send_mail(rec.id,force_send=True)
                _logger.info("The Email has sent successfully!!")


