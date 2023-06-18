$(document).ready(function () {
    var Kitchen_Name = $('.kitchen-name').val()
    var Kitchen_Number = $('.kitchen-mobile').val()
    var Kitchen_Type = $('.kitchen-type').val()
    var Kitchen_Open_Time = $('.kitchen-open-time').val()
    var Kitchen_Close_Time = $('.kitchen-close-time').val()
    var Kitchen_Address = $('.kitchen-street').val()
    var Kitchen_State = $('.kitchen-state').val()
    var Kitchen_City = $('.kitchen-city').val()
    var Kitchen_Country = $('.kitchen-country').val()
    var Kitchen_Pincode = $('.kitchen-pincode').val()

    $(".kitchen-name").change(function () {
        Kitchen_Name = $(this).val();
    });

    $(".kitchen-mobile").change(function () {
        Kitchen_Number = $(this).val();
    });

    $(".kitchen-type").change(function () {
        Kitchen_Type = $(this).val();
    });

    $(".kitchen-open-time").change(function () {
        Kitchen_Open_Time = $(this).val();
    });

    $(".kitchen-close-time").change(function () {
        Kitchen_Close_Time = $(this).val();
    });

    $(".kitchen-street").change(function () {
        Kitchen_Address = $(this).val();
    });

    $(".kitchen-state").change(function () {
        Kitchen_State = $(this).val();
    });

    $(".kitchen-city").change(function () {
        Kitchen_City = $(this).val();
    });

    $(".kitchen-country").change(function () {
        Kitchen_Country = $(this).val();
    });

    $(".kitchen-pincode").change(function () {
        Kitchen_Pincode = $(this).val();
    });


    $("body").on("click", ".kitchen-profile-button", function () {
        
        data = {
            "Kitchen_Name": Kitchen_Name,
            "Kitchen_Number": Kitchen_Number,
            "Kitchen_Type": Kitchen_Type,
            "Kitchen_Open_Time": Kitchen_Open_Time,
            "Kitchen_Close_Time": Kitchen_Close_Time,
            "Kitchen_Address": Kitchen_Address,
            "Kitchen_State": Kitchen_State,
            "Kitchen_City": Kitchen_City,
            "Kitchen_Country": Kitchen_Country,
            "Kitchen_Address": Kitchen_Address,
            "Kitchen_Pincode": Kitchen_Pincode
        }

        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5001/updateProfile',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                $(".kitchen-profile-button").prop('disabled', true);
                $(".kitchen-profile-button").html('Updated!');
            }
        });
    });
});