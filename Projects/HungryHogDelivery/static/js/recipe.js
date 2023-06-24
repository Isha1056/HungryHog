$(document).ready(function(){
    $(".recipe-button").click(function(){
        $(".recipe-button").prop('disabled', true);
        var json = {
            "INGREDIENTS":$('.recipe-input').val()
        }
        $('.recipe-input').val("");
        $(".recipe-container").empty();
        $(".recipe-container").append(`<div class="preloader"></div>`);
        
        $.ajax({
            type: 'post',
            url: 'http://127.0.0.1:5000/getrecipe',
            data: JSON.stringify(json),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                $(".recipe-container").empty();
                data = data['RECIPE']
                $(".recipe-button").removeAttr('disabled');
                console.log(typeof data, data);
                for(var i=0; i<data.length; i++) {
                    
                    const byteCharacters = atob(data[i]['Image']);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }
                    const byteArray = new Uint8Array(byteNumbers);
                    var imgurl = URL.createObjectURL(new Blob([byteArray], { type: 'image/png' }));
                    console.log(imgurl)
                    var c = i+1;
                    $(".recipe-container").append(`<div class="row clearfix">
                            <!--Content Column-->
                            <div class="content-column col-md-6 col-sm-12 col-xs-12">
                                <div class="inner-box">
                                    <!--Sec Title-->
                                    <div class="sec-title">
                                        <h2>`+c+`:</h2>
                                        <h3>`+data[i]['Title']+`</h3>
                                    </div>
                                    <div class="content">
                                        <!--<div class="text">sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</div>-->
                                        
                                        <!--Meeting Info-->
                                        <div class="meeting-info">
                                            <h4>Ingredients</h4>
                                            <div class="text">`+data[i]['Ingredients']+`</div>
                                        </div>
                                        
                                        <!--Meeting Info-->
                                        <div class="meeting-info">
                                            <h4>Directions</h4>
                                            <div class="text">`+data[i]['Directions']+`</div>
                                        </div>
                                        
                                        <a href="http://www.google.com/search?q=`+data[i]['Title']+`" class="read-more theme-btn btn-style-one" target="_blank">Know More</a>
                                    </div>
                                    
                                </div>
                            </div>
                            
                            <!--Image Column-->
                            <div class="image-column col-md-6 col-sm-12 col-xs-12">
                                <div class="row clearfix">
                                    <div class="column col-md-12 col-sm-12 col-xs-12">
                                        <figure class="image-box">
                                            <img src="`+imgurl+`" alt="" />
                                        </figure>
                                    </div>
                                </div>
                            </div>
                            
                        </div>
                        `);
                }
            }
        });
    });
  });