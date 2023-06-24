function getUserSignInDetails() {
  console.log("ready");
  let email = document.getElementById("user-email").innerHTML;
  console.log(email);
}

var latitude = 200;
var longitude = 200;

function showPosition(position) {
  latitude = position.coords.latitude;
  longitude = position.coords.longitude;
}


$(document).ready(function () {
  jQuery.support.cors = true;
  $(".user_signin_form").submit(function (e) {
    e.preventDefault();
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    console.log(email, password);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition);
    } 
    var senddata = {
      "Delivery_Partner_Email": email,
      "Delivery_Partner_Password": password,
      "Delivery_Partner_Latitude": latitude,
      "Delivery_Partner_Longitude": longitude
    };

    $.ajax({
      url: "http://127.0.0.1:5002/UsersAuthentication",
      method: "POST",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify(senddata),
      success: function (response) {
        console.log(response);
        if (response.StatusCode == 1){
          console.log("Signed in!")
          window.open("http://127.0.0.1:5002/", "_self")          
        }
        else{
          alert(response.ErrorMessage)
        }
      },
      error: function (xhr, status, error) {
        console.log(xhr, status, error);
      },
    });
  });
});
