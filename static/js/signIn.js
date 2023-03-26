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

        $.ajax({
            url: "http://127.0.0.1:5000/UsersAuthentication",
            method: "POST",
            dataType: "json",
            data: JSON.stringify({ 
                'USER_EMAIL': 'abc@gmail.com', 
                'USER_PASSWORD': 'Pass@123' 
            }),
            success: function(response) {
              console.log(response)
            },
            error: function(xhr, status, error) {
              console.log(xhr, status, error);
            }
          });
    });
});


