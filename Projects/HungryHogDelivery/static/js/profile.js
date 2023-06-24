$(document).ready(function () {
    var Delivery_Partner_Number = $('.deliverypartner-mobile').val()

    $(".deliverypartner-mobile").change(function () {
        Delivery_Partner_Number = $(this).val();
    });

    $("body").on("click", ".deliverypartner-profile-button", function () {
        
        data = {
            'Delivery_Partner_Number': Delivery_Partner_Number,
        }

        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5002/updateProfile',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                $(".deliverypartner-profile-button").prop('disabled', true);
                $(".deliverypartner-profile-button").html('Updated!');
            }
        });
    });
});