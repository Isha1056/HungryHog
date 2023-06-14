$(document).ready(function () {
    var USER_MOBILE = $('.user-mobile').val()
    var USER_STREET = $('.user-street').val()
    var USER_STATE = $('.user-state').val()
    var USER_CITY = $('.user-city').val()
    var USER_COUNTRY = $('.user-country').val()
    var USER_PINCODE = $('.user-pincode').val()

    $(".user-mobile").change(function () {
        USER_MOBILE = $(this).val();
    });

    $(".user-street").change(function () {
        USER_STREET = $(this).val();
    });

    $(".user-state").change(function () {
        USER_STATE = $(this).val();
    });

    $(".user-city").change(function () {
        USER_CITY = $(this).val();
    });

    $(".user-country").change(function () {
        USER_COUNTRY = $(this).val();
    });

    $(".user-pincode").change(function () {
        USER_PINCODE = $(this).val();
    });
    $("body").on("click", ".user-button", function () {
        
        data = {
            'USER_MOBILE': USER_MOBILE,
            'USER_STREET': USER_STREET,
            'USER_STATE': USER_STATE,
            'USER_CITY': USER_CITY,
            'USER_COUNTRY': USER_COUNTRY,
            'USER_PINCODE': USER_PINCODE
        }

        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5000/updateProfile',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                $(".user-button").prop('disabled', true);
                $(".user-button").html('Updated!');
            }
        });
    });
});