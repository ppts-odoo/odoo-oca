# Copyright 2013 Nicolas Bessi (Camptocamp SA)
# Copyright 2014 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2015 Grupo ESOC (<http://www.grupoesoc.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Helpdesk Website",
    "summary": "Helpdesk Website",
    "version": "12.0.1.0.1",
    "author": "PPTS [India] Pvt.Ltd.",
    "license": "LGPL-3",
    "maintainer": "PPTS [India] Pvt.Ltd.",
    "category": "Extra Tools",
    "website": "https://www.pptssolutions.com",
    "depends": ['base_setup','base','website'],
    "data": [
        'security/ir.model.access.csv',
        'data/website_config.xml',
        "views/master_menu_views.xml",
        "views/sub_menu_views.xml",
        "views/page_content_views.xml",
        "views/website_templates.xml",
    ],
    'images': ['static/description/banner.png'],
    "auto_install": False,
    "installable": True,
}
