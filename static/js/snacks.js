$(document).ready(function(){
    $(".order-button").click(function(){
        var id = $(this).attr('id');
        console.log(id);
        $(this).prop('disabled', true);
        $(this).text('Added');  
        var json = {
            "SNACK_ID":id
        }
        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5000/Shoping_cart',
            data: JSON.stringify(json),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                $(".count").text(parseInt($(".count").text())+1);
                
            }
        });
    });
  });

window.onbeforeunload = function() {
    $.ajax({
        type: 'GET',
        url: 'http://127.0.0.1:5000/updatecartcount',
        traditional: true,
        success: function (data) {
        }
    });
  }
  
  