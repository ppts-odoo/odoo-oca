# Copyright 2018 Camptocamp SA
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Multi Level BoM Stock",
    "summary": "By Using this module PDF report will be Generated With Multi BOMS and show the stock available in the Multi source location for multiple product variants  in two ways.Multi level BOM and Top level BOM.",
    "version": "14.0.1.0.0",
    "category": "Manufacture",
    "website": "https://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    "license": "AGPL-3",
    "depends": [
        "mrp_bom_location",
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/mrp_menu.xml",
        "reports/report_mrpcurrentstock.xml",
        "wizard/bom_route_current_stock_view.xml",
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
