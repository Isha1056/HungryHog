function getUserSignInDetails() {
  console.log("ready");
  let email = document.getElementById("user-email").innerHTML;
  console.log(email);
}

$(document).ready(function () {
  jQuery.support.cors = true;
  $(".user_signin_form").submit(function (e) {
    e.preventDefault();
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    console.log(email, password);

    var senddata = {
      USER_EMAIL: email,
      USER_PASSWORD: password,
    };

    $.ajax({
      url: "http://127.0.0.1:5000/UsersAuthentication",
      method: "POST",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify(senddata),
      success: function (response) {
        console.log(response);
        if (response.StatusCode == 1){
          localStorage.setItem('UserID', response.UserRecord.USER_ID);
          localStorage.setItem('UserName', response.UserRecord.USER_NAME);
          localStorage.setItem('UserEmail', response.UserRecord.USER_EMAIL);
          localStorage.setItem('UserMobile', response.UserRecord.USER_MOBILE);
          localStorage.setItem('UserAddress', response.UserRecord.USER_ADDRESS);
          
          window.open("http://127.0.0.1:5000/ordernow", "_self");
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
