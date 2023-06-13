$(document).ready(function () {
    $("body").on("click", ".review-button", function () {
        var myClass = $(this).attr("class").split(/\s+/);
        myClass.pop()
        Kitchen_ID = myClass.pop();

        reviewClass = myClass.concat(["review"]).join(".");
        ratingClass = myClass.concat(["rating"]).join(".");

        review = $("."+reviewClass).val();
        rating = $("."+ratingClass).find(":selected").val()

        console.log("."+ratingClass)

        if (rating == 0){
            $("."+ratingClass).css("border", "black solid 1px");
        } else {
            senddata = {
                "SNACK_RATING": rating,
                "SNACK_REVIEW": review,
                "SCHEDULE_TIME": myClass[1],
                "SNACK_ID": myClass[0],
                "Kitchen_ID": Kitchen_ID
            }
            $.ajax({
                url: "http://127.0.0.1:5000/ReviewSubmit",
                method: "POST",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify(senddata),
                success: function (response) {
                    console.log(response);
                    if (response.StatusCode == 1) {
                        console.log("Rating saved!")
                        $("."+myClass.join(".")).prop('disabled', true);
                        $("."+reviewClass).prop('disabled', true);
                        $("."+ratingClass).prop('disabled', true);
                    }
                    else {
                        alert(response.ErrorMessage)
                    }
                },
                error: function (xhr, status, error) {
                    console.log(xhr, status, error);
                },
            });
        }
    })
});
