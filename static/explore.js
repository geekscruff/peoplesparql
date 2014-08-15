$(document).ready(function(){

  $(".more").click(function() {

    var rev = $(".reveal");

    if (rev.css("display") == 'none') {
        $(".reveal").css("display", "block");
        $(".more").val('Show less');
        }
    else if (rev.css("display") == 'block') {
        $(".reveal").css("display", "none");
        $(".more").val('More details');
        }
  });

});