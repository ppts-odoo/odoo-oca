odoo.define('purchase.requisition', function (require) {
'use strict';
	var Model = require('web.Model');
	$(function(){
	    $("button").mouseenter(function() {

	        var values = $(this).val();
			var res = values.split(",");
			var value=res[2];
			var value1=res[1];
	        return new Model("purchase.requisition").call('show_terms_condition',[parseInt(value), value1, parseInt(value)])
	           .then(function(action){
	           if (action){
	           		document.getElementById('my_vals').innerHTML = action;
	           		var modal = document.getElementById('myModal');
	           		modal.style.display = "block";
	           }
	           else{
	           	document.getElementById('my_vals').innerHTML = 'Notes Unavailable';
	           	var modal = document.getElementById('myModal');
	           	modal.style.display = "block";
	           }
	           });
	    });
	    var span = document.getElementsByClassName("close")[0];
	    var modal = document.getElementById('myModal');
		span.onclick = function() {
   			modal.style.display = "none";
		}
		window.onclick = function(event) {
		    if (event.target == modal) {
		        modal.style.display = "none";
		    }
		}
	});
});