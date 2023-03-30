function create_tr(table_id) {
  let table_body = document.getElementById(table_id),
    first_tr = table_body.firstElementChild;
  tr_clone = first_tr.cloneNode(true);

  table_body.append(tr_clone);

  clean_first_tr(table_body.firstElementChild);
}

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
    // console.log(val);
    $(this)
      .prev(".prod_qty")
      .val(val * 1 + 1);
  });

  $("body").on("click", ".quantity-spinner .minus", function () {
    var val = $(this).next(".prod_qty").val();
    if (val != 1) {
      $(this)
        .next(".prod_qty")
        .val(val * 1 - 1);
    }
  });
});

function remove_tr(This) {
  if (This.closest("tbody").childElementCount == 1) {
    This.closest("tr").remove();
    $("#table-outer").hide();
    var empty = `<h3>Snort! your shopping cart is empty. Please select meals to add in your tiffin</h3>`;
    $("#cart-outer").append(empty);
  } else {
    This.closest("tr").remove();
  }
}
function calculateTotal(price, quantity) {
  return price * quantity;
}

$(function () {
  $.ajax({
    type: "GET",
    url: "http://127.0.0.1:5000/Shoping_cart",
    contentType: "application/json",
    success: function (result, status, xhr) {
      // console.log(result);
      sampleData = result.ShoppingCartList;
      var tabledata = result.ShoppingCartList;
      console.log(tabledata);
      var tablerow = "";
      $.each(tabledata, function (key, value) {
        console.log("key: " + key);
        tablerow +=
          `<tbody id="table_body">
        <tr>
            <td colspan="2" class="prod-column">
                <div class="column-box">
                    <figure class="prod-thumb"><a href="#"><img
                                src="` +
          tabledata[key].PRODUCT_LOGO +
          `"
                                alt=""></a></figure>
                    <h4 class="prod-title">` +
          tabledata[key].PRODUCT_NAME +
          `</h4>
                </div>
            </td>
            <td class="price">Rs. ` +
          tabledata[key].PRODUCT_PRICE +
          `</td>
            <td class="qty">
                <div class="quantity-spinner"><button type="button" class="minus"><span
                            class="fa fa-minus"></span></button><input type="text"
                        name="product" value="1" class="prod_qty" /><button type="button"
                        class="plus"><span class="fa fa-plus"></span></button></div>
            </td>
          <td class="kitchenname">` +
          tabledata[key].Kitchen_Name +
          `</td>
          <td class="schedule"></td>
          <td class="total"></td>
            <td>
                <div class="action_container">
                    <button class="danger" onclick="remove_tr(this)">
                        <i class="fa fa-close"></i>
                    </button>
                </div>
            </td>
        </tr>
    </tbody>`;
      });
      $("._table").append(tablerow);
    },
  });
});
