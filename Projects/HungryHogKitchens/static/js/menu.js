File.prototype.convertToBase64 = function (callback) {
    var reader = new FileReader();
    reader.onloadend = function (e) {
        console.log(e.target.result)
        callback(e.target.result, e.target.error);
    };
    reader.readAsDataURL(this);
};

$(document).ready(function () {

    $("body").on("click", ".saveSnack", function () {
        if ($(this).closest('tr').find('.input-image').get(0).files.length == 0) {
            $(this).closest('tr').find('.input-image').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-name').val() == "") {
            $(this).closest('tr').find('.input-name').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-price').val() == "") {
            $(this).closest('tr').find('.input-price').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-mealtype').val() == "") {
            $(this).closest('tr').find('.input-mealtype').css('border', '3px solid red');
        } else {
            var form_data = new FormData();
            form_data.append('SNACK_LOGO', $(this).closest('tr').find('.input-image').get(0).files[0]);
            form_data.append('SNACK_NAME', $(this).closest('tr').find('.input-name').val());
            form_data.append('SNACK_PRICE', $(this).closest('tr').find('.input-price').val());
            form_data.append('Meal_ID', $(this).closest('tr').find('.input-mealtype').val());
            x = $(this);
            x.attr('disabled', true);
            $.ajax({
                type: 'POST',
                url: 'http://127.0.0.1:5001/SaveSnack',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function (data) {
                    console.log("Snack saved!");
                    x.closest('tr').attr('class', data["SNACK_ID"]);
                    x.removeAttr("disabled");
                },
            });
        }
    });


    $("body").on("click", ".updateSnack", function () {
        if ($(this).closest('tr').find('.input-image').get(0).files.length == 0) {
            $(this).closest('tr').find('.input-image').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-name').val() == "") {
            $(this).closest('tr').find('.input-name').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-price').val() == "") {
            $(this).closest('tr').find('.input-price').css('border', '3px solid red');
        } else if ($(this).closest('tr').find('.input-mealtype').val() == "") {
            $(this).closest('tr').find('.input-mealtype').css('border', '3px solid red');
        } else {

            var form_data = new FormData();
            form_data.append('SNACK_ID', $(this).closest('tr').attr('class'));
            form_data.append('SNACK_LOGO', $(this).closest('tr').find('.input-image').get(0).files[0]);
            form_data.append('SNACK_NAME', $(this).closest('tr').find('.input-name').val());
            form_data.append('SNACK_PRICE', $(this).closest('tr').find('.input-price').val());
            form_data.append('Meal_ID', $(this).closest('tr').find('.input-mealtype').val());
            x = $(this);
            x.attr('disabled', true);
            $.ajax({
                type: 'POST',
                url: 'http://127.0.0.1:5001/UpdateSnack',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function (data) {
                    console.log("Snack saved!");
                    x.closest('tr').attr('class', data["SNACK_ID"]);
                    x.removeAttr("disabled");
                },
            });
        }
    });


    $("body").on('change', ".input-image", function () {
        var image_object_url = URL.createObjectURL($(this).get(0).files[0]);
        $(this).closest('tr').find('.snack-image').attr('src', image_object_url).show();
    });


    $("body").on("click", ".removeSnack", function () {
        var SNACK_ID = $(this).closest('tr').attr('class');
        if (typeof SNACK_ID !== "undefined") {

            var postData = {
                "SNACK_ID": SNACK_ID
            }
            x = $(this)
            $.ajax({
                type: 'post',
                url: 'http://127.0.0.1:5001/RemoveSnack',
                data: JSON.stringify(postData),
                contentType: "application/json; charset=utf-8",
                traditional: true,
                success: function (data) {
                    x.closest('tr').remove();
                }
            });
        }
        else {
            $(this).closest('tr').remove();
        }
    });

});