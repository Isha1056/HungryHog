$(document).ready(function(){

    function showPosition(position) {
        //x.innerHTML = "Latitude: " + position.coords.latitude + 
        //"<br>Longitude: " + position.coords.longitude;
        var data = {
            "USER_LATITUDE": position.coords.latitude,
            "USER_LONGITUDE": position.coords.longitude
        };
        console.log(data);
        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5000/updateUserCoordinates',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
              console.log(data)
            }
          });
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } 

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
