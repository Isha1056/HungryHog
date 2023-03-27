function create_tr(table_id) {
    let table_body = document.getElementById(table_id),
        first_tr   = table_body.firstElementChild
        tr_clone   = first_tr.cloneNode(true);

    table_body.append(tr_clone);

    clean_first_tr(table_body.firstElementChild);
}

function clean_first_tr(firstTr) {
    let children = firstTr.children;
    
    children = Array.isArray(children) ? children : Object.values(children);
    children.forEach(x=>{
        if(x !== firstTr.lastElementChild)
        {
            x.firstElementChild.value = '';
        }
    });
}


function remove_tr(This) {
    if(This.closest('tbody').childElementCount == 1)
    {
        This.closest('tr').remove();
        $("#table-outer").hide();
        var empty = `<h3>Snort! your shopping cart is empty. Please select meals to add in your tiffin</h3>`;
        $("#cart-outer").append(empty);
    }else{
        This.closest('tr').remove();
    }
}


$(function() {
    $.ajax({
        type: "GET",
        url: "{{url_for('getKitchens')}}",
        contentType: "application/json",
        success: function (result, status, xhr) {
            // console.log(result);
            sampleData = result.get_kitchens;
            var tabledata = result.get_kitchens;
            // console.log(tabledata);
            var tablerow = '';
            tablerow += `<table class="table table-striped table-bordered table-hover" style id="dataTable" data-toggle="table" data-search="true" data-side-pagination="server" data-pagination="true">
            <thead>
                <tr>
                <th data-field="PRODUCT_ID">Kitchen_ID</th>
                <th data-field="Kitchen_Name">Kitchen_Name</th>
                <th data-field="Kitchen_Type">Kitchen_Type</th>
                <th data-field="Kitchen_open_time">Kitchen_open_time</th>
                <th data-field="Kitchen_Close_time">Kitchen_Close_time</th>
                <th data-field="Kitchen_Number">Kitchen_Number</th>
                <th data-field="Meal_ID">Meal_ID</th>
                <th data-field="Popularity">Popularity</th>
                <th data-field="Kitchen_Address">Kitchen_Address</th>
                </tr>
            </thead><tbody>`
            $.each(tabledata, function (key, value) {
                console.log("key: " + key);
                tablerow += '<tr class="' + key + '" id="rownum' + key + '">';
                tablerow += '<td>' + value.Kitchen_ID + '</td>';
                tablerow += '<td>' + value.Kitchen_Name + '</td>';
                tablerow += '<td>' + value.Kitchen_Type + '</td>';
                tablerow += '<td>' + value.Kitchen_open_time + '</td>';
                tablerow += '<td>' + value.Kitchen_Close_time + '</td>';
                tablerow += '<td>' + value.Kitchen_Number + '</td>';
                tablerow += '<td>' + value.Meal_ID + '</td>';
                tablerow += '<td>' + value.Popularity + '</td>';
                tablerow += '<td>' + value.Kitchen_Address + '</td>';

            });
            $('.card-body1').append(tablerow);
            $('#dataTable').DataTable();
        }
    });
});