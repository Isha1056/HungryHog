function create_tr(table_id) {
  let table_body = document.getElementById(table_id),
    first_tr = table_body.firstElementChild;
  tr_clone = first_tr.cloneNode(true);

  table_body.append(tr_clone);

  clean_first_tr(table_body.firstElementChild);
}

let price = 0;
let totalAmount = [];

function clean_first_tr(firstTr) {
  let children = firstTr.children;

  children = Array.isArray(children) ? children : Object.values(children);
  children.forEach((x) => {
    if (x !== firstTr.lastElementChild) {
      x.firstElementChild.value = "";
    }
  });
}

$(function() {
  $("body").on("click", ".Checkout", function () {
    $(".checkout-clearfix").show();
    var amt = calculateOrderTotal();
    $(".total-amount").append(amt);
  });
  $(".checkout-clearfix").hide();
});

$("body").on("click", ".removeOrder", function () {
  var count = $('._table tr').length;
  if (count <= 2) {
    $('._table').remove();
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
  console.log(price, quantity);
  return price * quantity;
}

function calculateOrderTotal(){
  var sum = 0;
  var iPrice = 0;
  $('._table tbody tr').each(function () {
    iPrice  = $(this).find('td').eq(5).text() || 0,
    qty = +$(this).find('.price').val() || 0,
    iPrice = parseInt(iPrice);
    sum = sum + (iPrice);
  });
  return sum;
  console.log("total: ",sum);
}
