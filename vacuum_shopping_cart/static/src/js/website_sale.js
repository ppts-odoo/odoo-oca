$(document).ready(function () {
odoo.define('website_sale.website_sale_control', function (require) {
    "use strict";
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    var ajax = require('web.ajax');
    $(oe_website_sale).on("click", ".oe_cart .oe_clear_shopping_cart", function () {
        ajax.jsonRpc("/shop/clear_cart", "call", {}).then(function(){
            location.reload();
        });
        return false;
    });
});
});
});