# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Multi Level BoM Stock",
    "summary": "Adds location field to Bill of Materials and its components.",
    "version": "12.0.1.0.1",
    "category": "Manufacture",
    "website": "https://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "mrp","base",
    ],
    "data": [
        "views/mrp_view.xml",
        "views/report_mrpbomstructure.xml",
    ],
    "installable": True
}
