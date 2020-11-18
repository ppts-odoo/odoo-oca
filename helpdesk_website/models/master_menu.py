# Copyright 2013 Nicolas Bessi (Camptocamp SA)
# Copyright 2014 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2015 Grupo ESOC (<http://www.grupoesoc.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, fields, models, tools, SUPERUSER_ID
_logger = logging.getLogger(__name__)

class MasterMenu(models.Model):

    _name = "master.menu"
    _description = "Master Menu"
    
    name = fields.Char("Name", required=True, copy=False)

     
     
    
    
    
    
    
    

