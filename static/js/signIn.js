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
      },
      error: function (xhr, status, error) {
        console.log(xhr, status, error);
      },
    });
  });
});
