function create_tr(table_id) {
  let table_body = document.getElementById(table_id),
    first_tr = table_body.firstElementChild;
  tr_clone = first_tr.cloneNode(true);

  table_body.append(tr_clone);

  clean_first_tr(table_body.firstElementChild);
}

let price = 0;

function clean_first_tr(firstTr) {
  let children = firstTr.children;

  children = Array.isArray(children) ? children : Object.values(children);
  children.forEach((x) => {
    if (x !== firstTr.lastElementChild) {
      x.firstElementChild.value = "";
    }
  });
}

$(document).ready(function () {
  $("body").on("click", ".quantity-spinner .plus", function () {
    var val = $(this).prev(".prod_qty").val();
    price = $(this).closest('tr').find('.price').text();
    price = parseInt(price);
    console.log(price, typeof (price));
    $(this).prev(".prod_qty").val(val * 1 + 1);
    $(this).closest('tr').find('.total').text(calculateTotal(price, parseInt(val * 1 + 1)));
  });

  $("body").on("click", ".quantity-spinner .minus", function () {
    var val = $(this).next(".prod_qty").val();
    if (val != 1) {
      $(this).next(".prod_qty").val(val * 1 - 1);
      $(this).closest('tr').find('.total').text(calculateTotal(price, parseInt(val * 1 - 1)));
    }
  });
});

$("body").on("click", ".removeOrder", function () {
  var count = $('._table tr').length;
  if (count <= 2) {
    $('._table').remove();
    // if ($(this).closest("tbody").childElementCount == 1) {
    //   $(this).closest("tr").remove();
    //   $("#table-outer").hide();
    var empty = `<h3>Snort! your shopping cart is empty. Please select meals to add in your tiffin</h3>`;
    $("#cart-outer").append(empty);
  } else {
    $(this).closest("tr").remove();
  }
  var PRODUCT_ID = $(this).closest('tr').find('.productID').text();
  console.log(PRODUCT_ID);
  delProductId = {
    PRODUCT_ID: PRODUCT_ID
  }
  $.ajax({
    type: 'post',
    url: 'http://127.0.0.1:5000/deleteCartRow',
    data: JSON.stringify(delProductId),
    contentType: "application/json; charset=utf-8",
    traditional: true,
    success: function (data) {
      console.log("Data deleted!")
    }
  });
});

function calculateTotal(price, quantity) {
  return price * quantity;
}

// $(function () {

//   $.ajax({
//     type: "GET",
//     url: "http://127.0.0.1:5000/Shoping_cart",
//     contentType: "application/json",
//     success: function (result, status, xhr) {
//       // console.log(result);
//       sampleData = result.ShoppingCartList;
//       var tabledata = result.ShoppingCartList;
//       console.log(tabledata);
//       var tablerow = "";
//       $.each(tabledata, function (key, value) {
//         tablerow +=
//           `<tbody id="table_body">
//         <tr>
//             <td class="productID" style="display:none;">`+ tabledata[key].PRODUCT_ID + `</td>
//             <td colspan="2" class="prod-column">
//                 <div class="column-box">
//                     <figure class="prod-thumb"><a href="#"><img
//                                 src="` + tabledata[key].PRODUCT_LOGO + `"alt=` + tabledata[key].PRODUCT_LOGO + `"></a></figure>
//                     <h4 class="prod-title">` +
//           tabledata[key].PRODUCT_NAME +
//           `</h4>
//                 </div>
//             </td>
//             <td class="price">` +
//           tabledata[key].PRODUCT_PRICE +
//           `</td>
//             <td class="qty">
//                 <div class="quantity-spinner"><button type="button" class="minus"><span
//                             class="fa fa-minus"></span></button><input type="text"
//                         name="product" value="1" class="prod_qty" /><button type="button"
//                         class="plus"><span class="fa fa-plus"></span></button></div>
//             </td>
//           <td class="kitchenname">` +
//           tabledata[key].Kitchen_Name +
//           `</td>
//           <td class="total">Rs. `+ parseInt(tabledata[key].PRODUCT_PRICE) + `</td>
//             <td>
//                 <div class="action_container">
//                     <button class="danger removeOrder">
//                         <i class="fa fa-close"></i>
//                     </button>
//                 </div>
//             </td>
//         </tr>
//     </tbody>`;
//       });
//       $("._table").append(tablerow);
//     },
//   });

//   var count = $('._table tr').length;
//   if (count <= 2 && tabledata == '') {
//     $('._table').hide();
//     var empty = `<h3>Snort! your shopping cart is empty. Please select meals to add in your tiffin</h3>`;
//     $("#cart-outer").append(empty);
//   }
//   else{
//     $('._table').show();
//     $("#cart-outer").remove(empty);
//   }
// });
