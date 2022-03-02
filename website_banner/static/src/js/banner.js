
$(document).ready(function(){
 
	 $.ajax({ 
             url: "/home",                 
            success: function(result){
            result_new_serial=result.split(",,,");
            $("#wrapwrap").before('<div class="container" id="banner" style="text-align:center">'+result_new_serial[0]+'</div>');
            document.getElementById("banner").style.background=result_new_serial[1];
            document.getElementById("text").style.color=result_new_serial[2];
            document.getElementById("text2").style.color=result_new_serial[2];
            document.getElementById("button").style.background=result_new_serial[3];
	    document.getElementById("button").style.color=result_new_serial[4];
                },
            });
 
//EOF
});
