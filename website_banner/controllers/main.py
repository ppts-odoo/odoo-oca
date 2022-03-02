from odoo import http
from odoo.http import request
from datetime import timedelta, datetime

class WebsiteBanner(http.Controller):
	@http.route('/home', type='http', auth="public", website=True)
	def index(self, **kw):
		promos=request.env['promotion.setup'].search([])
		cont=''
		# current_date = datetime.today().date()

		current_date = datetime.strptime(str(datetime.today().strftime("%Y-%m-%d %H:%M:%S")), '%Y-%m-%d %H:%M:%S')
		if promos:
			for promo in promos:
				start_date = datetime.strptime(str(promo.start_date), '%Y-%m-%d %H:%M:%S')
				end_date = datetime.strptime(str(promo.end_date), '%Y-%m-%d %H:%M:%S')
				bg_color = promo.bg_color
				text_color = promo.text_color
				btn_color = promo.btn_color
				btn_txt_color = promo.btn_txt_color
				if current_date >= start_date and current_date <= end_date:
					cont+="""
						<h2 id="text" style="text-align:center">"""+str(promo.name)+"""</h1>      
					    <p id="text2" style="text-align:center">"""+str(promo.text_to_display)+"""</p>
					    <a href='"""+str(promo.url)+"""' class="btn btn-primary" id="button" style="text-align:center" >Click to View</a>
					    <br /><br />
					"""

		return cont+',,,'+bg_color+',,,'+text_color+',,,'+btn_color+',,,'+btn_txt_color
	
	
	
	
	
