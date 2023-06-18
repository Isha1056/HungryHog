var Kitchen_Request = 1;

function showPosition(position) {
    //x.innerHTML = "Latitude: " + position.coords.latitude + 
    //"<br>Longitude: " + position.coords.longitude;
    var data = {
        "Kitchen_Latitude": position.coords.latitude,
        "Kitchen_Longitude": position.coords.longitude,
        "Kitchen_Request": USER_REQUEST
    };
    //console.log(data);
    $.ajax({
        type: 'post',
        url: 'http://127.0.0.1:5001/updateKitchenCoordinates',
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            $(".use-current-location").text("Using Current Location")
          //console.log(data)
        }
      });
}

$(document).ready(function(){
    

    if (navigator.geolocation) {
        Kitchen_Request = 1;
        navigator.geolocation.getCurrentPosition(showPosition);
    } 

    $(".logout").click(function(){
        $.ajax({
            type: 'get',
            url: 'http://127.0.0.1:5001/logout',
            traditional: true,
            success: function (data) {
                //console.log("Logged Out!");
                window.open("http://127.0.0.1:5001/", "_self")
            }
        });
    });

    $("body").on("click", ".use-current-location", function(e) {
        e.preventDefault();
        if (navigator.geolocation) {
            Kitchen_Request = 0;
            navigator.geolocation.getCurrentPosition(showPosition);
        }
    });

  });
