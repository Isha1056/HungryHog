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
        url: "http://127.0.0.1:5000/Shoping_cart",
        contentType: "application/json",
        success: function (result, status, xhr) {
            // console.log(result);
            sampleData = result.ShoppingCartList;
            var tabledata = result.ShoppingCartList;
            // console.log(tabledata);
            var tablerow = '';
            tablerow += `<table class="table table-striped table-bordered table-hover" style id="dataTable" data-toggle="table" data-search="true" data-side-pagination="server" data-pagination="true">
            <thead>
                <tr>
                <th data-field="PRODUCT_NAME">PRODUCT</th>
                <th data-field="PRODUCT_LOGO">PRODUCT_LOGO</th>
                <th data-field="PRODUCT_PRICE">PRICE</th>
                <th data-field="QUANTITY">QUANTITY</th>
                <th data-field="SCHEDULE_TIME">SCHEDULE</th>
                <th data-field="Kitchen_Name">KITCHEN</th>
                <th data-field="TOTAL_AMOUNT">TOTAL_AMOUNT</th>
                <th data-field="Meal_Type">Meal Type</th>
                </tr>
            </thead><tbody>`
            $.each(tabledata, function (key, value) {
                console.log("key: " + key);
                tablerow += '<tr class="' + key + '" id="rownum' + key + '">';
                tablerow += '<td>' + value.PRODUCT_NAME + '</td>';
                tablerow += '<td>' + value.PRODUCT_LOGO + '</td>';
                tablerow += '<td>' + value.PRODUCT_PRICE + '</td>';
                tablerow += '<td>' + value.QUANTITY + '</td>';
                tablerow += '<td>' + value.SCHEDULE_TIME + '</td>';
                tablerow += '<td>' + value.Kitchen_Name + '</td>';
                tablerow += '<td>' + value.TOTAL_AMOUNT + '</td>';
                tablerow += '<td>' + value.Meal_Type + '</td>';

            });
            $('.card-body1').append(tablerow);
            $('#dataTable').DataTable();
        }
    });
});