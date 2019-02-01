from odoo import http
from odoo.http import request
from datetime import datetime



class PipelineWebReport(http.Controller):
    @http.route(['/pipeline_report/pipeline_report_web_view/'], type='http', auth='public', website=True)
    def view_pipeline_report(self,**post):
#         print request.session['user_list']
        # print request.session['lead_ids']
        results = []
        user_ids = request.env['res.users'].sudo().search([('id','in', request.session['user_list'])])
#         print user_ids,"user_ids"
        stage_ids = request.env['crm.stage'].sudo().search([('id', 'in', request.session['stage_ids'])])
#         print stage_ids,"stage_ids"
        for user in user_ids:
            stage_values = []
            for stage in stage_ids:
                lead_ids = request.env['crm.lead'].sudo().search([('user_id', '=', user.id), ('stage_id', '=', stage.id)])
                stage_values.append({'stage': stage, 'leads': lead_ids})
            results.append({'user': user, 'stage_values': stage_values})

        return_values = {
            'date': datetime.today().date(),
            'users':user_ids,
            'stages':stage_ids,
            'results':results
        }
#         print return_values

        return request.render('pipeline_report.pipeline_report_web_view', return_values)

