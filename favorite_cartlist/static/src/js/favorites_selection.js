$(document).ready(function(){
$("#alert_me").hide();
$("#null_me").hide();
$("#favorites").change(function() {
  if ($(this).val() == "create_new_fav") {
    $('#favorites_name').show();
  } else {
    $('#favorites_name').hide();
    $('#favorite_name').removeAttr('required');
    $('#favorite_name').val('');
  }
});

$('#submit').click(function() {
    var x = document.getElementById("favorite_name").value;
    var y = document.getElementById("sale_order").value;
	    $.ajax({
	        url: "/check_favorites",
	        type: 'POST',
	        data: {x,y},
	        success: function(result) {
	        	if (result == 'True') {
	        		$("#alert_me").show();
	        	}
				else if (result == 'Null'){
					$("#alert_me").hide();
					$("#null_me").show();
					return false
				}
	        },
	    });
	});

$('#selectall').change(function () {
    if ($(this).prop('checked')) {
    $('input').prop('checked', true);
    }
    else {
        $('input').prop('checked', false);
    }
});
$('#selectall').trigger('change');

$('.delete_favorites').click(function(){
	var anyBoxesChecked = false;
	$('#delete_favorites_form input[type="checkbox"]').each(function() {
        if ($(this).is(":checked")) {
        	var boxes = ($(this).attr('class'));
        	if (boxes != undefined) {
        	 $.ajax({
     	        url: "/delete_favorites",
     	        type: 'POST',
     	        data: {boxes},
     	        success: function(result) {
     	        	if (result == 'True') {
    	        		window.location.href="/remove";
    	        	}
     	        }
     	    });
        	anyBoxesChecked = true;
    		$("input[type=checkbox]:checked").closest("tr").remove();
        	}
        }
    });
 
    if (anyBoxesChecked == false) {
      alert('Please select at least one product');
      return false;
    } 
});


$('#selectall_list').change(function () {
    if ($(this).prop('checked')) {
    $('input').prop('checked', true);
    }
    else {
        $('input').prop('checked', false);
    }
});
$('#selectall_list').trigger('change');

$('.delete_favorites_list').click(function(){
	var anyBoxesChecked = false;
	$('#delete_favorites_list_form input[type="checkbox"]').each(function() {
        if ($(this).is(":checked")) {
        	var boxes = ($(this).attr('class'));
        	if (boxes != undefined) {
        	 $.ajax({
     	        url: "/delete_favorites_list",
     	        type: 'POST',
     	        data: {boxes},
     	        success: function(result) {
     	        	if (result == 'True') {
    	        		window.location.href="/remove";
    	        	}
     	        }
     	    });
        	anyBoxesChecked = true;
    		$("input[type=checkbox]:checked").closest("tr").remove();
        	}
        }
    });
 
    if (anyBoxesChecked == false) {
      alert('Please select at least one product');
      return false;
    } 
});

$('#add_to_cart').click(function() {
	var sale_order_id = document.getElementById("sale_order").value;
    var favorite_id = document.getElementById("favorite_products").value;
	    $.ajax({
	        url: "/add_to_cart_favorites",
	        type: 'POST',
	        data: {sale_order_id,favorite_id},
	        success: function(result) {
	        	if (result == 'True') {
	        		window.location.href="/shop/cart";
	        	}
	        }
	    });
	});


});