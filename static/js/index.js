$(document).ready(function(){
    $(".logout").click(function(){
        $.ajax({
            type: 'get',
            url: 'http://127.0.0.1:5000/logout',
            traditional: true,
            success: function (data) {
                console.log("Logged Out!");
                window.open("http://127.0.0.1:5000/", "_self")
            }
        });
    });
  });
