//On Keyup function when searching a product
odoo.define('product_web_custom', function (require) {
"use strict";
var ajax = require('web.ajax');

$(document).ready(function ()
	{
	$("input[name='search']").keyup(function() {
		
		var category = $('.website_category').val();
		ajax.jsonRpc("/shop/get_products_list", 'call', {'search_value':$(this).val(), 'search_category':category})
		.then(function (data) {
			$('.search_lists').show();
			$('.search_lists').html('');
        	$('.search_lists').append(data);
                    
        });
	});

	if ($('.oe_website_sale .dropdown_sorty_by').length) {
            // this method allow to keep current get param from the action, with new search query
            $('.search_new').on('click', function (event) {
                var $this = $(this);
                if (!event.isDefaultPrevented() && !$this.is(".disabled")) {
                    event.preventDefault();
                    var oldurl = $('.mb-2').attr('action');
                    oldurl += (oldurl.indexOf("?")===-1) ? "?" : "";
                    var search = $('input.search-query');
					var website_category = $('.website_category')
                    window.location = oldurl + '&website_category='+ encodeURIComponent(website_category.val())+'&' + search.attr('name') + '=' + encodeURIComponent(search.val());
                }
            });
        }
});
});
